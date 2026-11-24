"""CiteCheck core — pure stdlib, no Flask needed.

The hard rule: an answer is only given when it can be quoted from the
uploaded notes. Otherwise CiteCheck refuses, instead of guessing.

Pipeline: text -> chunks (with source + chunk id) -> TF-IDF retrieval
-> quote-or-refuse answer -> 5-question quiz -> stale-date flags.

NOTE (honest limitation, see README): the Round 2 deck promised
TensorFlow embeddings. This build uses TF-IDF retrieval instead —
TensorFlow is not installed on this machine and the prototype must run
offline on the jury laptop. The retrieval interface is a single function
(`retrieve`), so TF embeddings can be swapped in without touching the
answer/quiz/stale logic. Do NOT claim TF embeddings in the demo.
"""

import math
import random
import re
import zlib
from collections import Counter

STOPWORDS = set(
    """a an the and or of to in on for is are was were be been it its this that
    with as by at from into about over under after before between through
    when while which who whom what how why where there here not no yes if
    then than so such can could will would should may might must have has
    had do does did i you he she we they them his her their our your my me
    him us""".split()
)

# A chunk whose best retrieval score is below this is treated as
# "not in the notes" and the answer is a refusal.
REFUSAL_THRESHOLD = 0.08

# Dates before this are flagged "possibly stale" in the demo.
STALE_CUTOFF_YEAR = 2024

_MONTHS = (
    "january february march april may june july august september october "
    "november december"
).split()
_DATE_RE = re.compile(
    r"\b(\d{1,2}\s+(?:%s)\s+\d{4}|(?:%s)\s+\d{4}|\d{4})\b"
    % ("|".join(_MONTHS), "|".join(_MONTHS)),
    re.IGNORECASE,
)


def tokenize(text):
    return [
        w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS
    ]


def chunk_text(text, source, max_words=120):
    """Split notes into chunks, keeping source + chunk id for citations."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    for para in paras:
        words = para.split()
        for i in range(0, len(words), max_words):
            piece = " ".join(words[i : i + max_words])
            chunks.append(
                {
                    "id": len(chunks) + 1,
                    "source": source,
                    "text": piece,
                }
            )
    return chunks


def _tfidf_vectors(chunks):
    docs = [Counter(tokenize(c["text"])) for c in chunks]
    n = len(docs)
    df = Counter()
    for d in docs:
        for term in d:
            df[term] += 1
    idf = {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}
    vecs = []
    for d in docs:
        vec = {t: (count / sum(d.values())) * idf[t] for t, count in d.items()}
        vecs.append(vec)
    return vecs, idf


def _cosine(a, b):
    dot = sum(a.get(t, 0.0) * v for t, v in b.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve(question, chunks, top_k=3):
    """Return [(score, chunk), ...] best-first. Empty list if no chunks."""
    if not chunks:
        return []
    vecs, idf = _tfidf_vectors(chunks)
    q = Counter(tokenize(question))
    if not q:
        return []
    qvec = {t: (c / sum(q.values())) * idf.get(t, 1.0) for t, c in q.items()}
    scored = sorted(
        ((_cosine(qvec, v), c) for v, c in zip(vecs, chunks)),
        key=lambda s: -s[0],
    )
    return scored[:top_k]


def answer(question, chunks):
    """Quote-or-refuse. Returns dict with answer/refusal + citations."""
    results = retrieve(question, chunks, top_k=3)
    if not results or results[0][0] < REFUSAL_THRESHOLD:
        return {
            "answered": False,
            "answer": "Not in your notes — I can't cite this, so I won't answer it.",
            "citations": [],
            "score": results[0][0] if results else 0.0,
        }
    # Quote the best supporting chunk verbatim (first 2 sentences),
    # plus the next-best chunk as a second citation when it is close.
    top = [c for s, c in results if s >= REFUSAL_THRESHOLD][:2]
    quotes = []
    for c in top:
        sentences = re.split(r"(?<=[.!?])\s+", c["text"])
        clean = [re.sub(r"^#+\s*", "", s).strip() for s in sentences]
        clean = [s for s in clean if len(s.split()) >= 3]
        if clean:
            quotes.append(" ".join(clean[:2]))
    return {
        "answered": True,
        "answer": " ".join(quotes),
        "citations": [
            {"source": c["source"], "chunk": c["id"]} for c in top
        ],
        "score": results[0][0],
    }


def make_quiz(chunks, n=5, seed=7):
    """5-question quiz from the notes. Each question blanks one key term
    from a chunk sentence; options are that term + 3 distractors taken
    from other chunks, so every correct answer is in the notes."""
    rng = random.Random(seed)
    if len(chunks) < n:
        return []
    order = list(chunks)
    rng.shuffle(order)
    # Distractor pool: distinctive terms from quiz-eligible chunks only
    # (heading chunks are excluded, so header words like "ronit" from the
    # sample file's title line never appear as quiz options).
    pool = sorted(
        {
            w
            for c in chunks
            if not c["text"].strip().startswith("#")
            for w in tokenize(c["text"])
            if len(w) > 4
        }
    )
    questions = []
    for c in order:
        if len(questions) >= n:
            break
        if c["text"].strip().startswith("#"):
            continue  # headings are not quiz material
        sentences = [
            s for s in re.split(r"(?<=[.!?])\s+", c["text"]) if len(s.split()) >= 6
        ]
        if not sentences:
            continue
        sentence = rng.choice(sentences)
        candidates = [w for w in tokenize(sentence) if len(w) > 4]
        if not candidates:
            continue
        term = rng.choice(candidates)
        distractors = [w for w in pool if w != term]
        rng.shuffle(distractors)
        options = sorted([term] + distractors[:3])
        blanked = re.sub(
            r"\b%s\b" % re.escape(term), "_____", sentence, count=1,
            flags=re.IGNORECASE,
        )
        questions.append(
            {
                "question": blanked,
                "options": options,
                "answer": term,
                "citation": {"source": c["source"], "chunk": c["id"]},
            }
        )
    return questions[:n]


def stale_flags(chunks):
    """Flag chunks that cite dates before STALE_CUTOFF_YEAR — the note
    may be out of date and the student should verify it."""
    flags = []
    for c in chunks:
        years = set()
        for m in _DATE_RE.finditer(c["text"]):
            ym = re.search(r"\d{4}", m.group(0))
            if ym:
                years.add(int(ym.group(0)))
        old = [y for y in years if y < STALE_CUTOFF_YEAR]
        if old:
            flags.append(
                {
                    "source": c["source"],
                    "chunk": c["id"],
                    "years": sorted(old),
                    "note": "Mentions %s — check whether this is still current."
                    % ", ".join(str(y) for y in sorted(old)),
                    "text": c["text"][:160],
                }
            )
    return flags


def extract_pdf_text(data):
    """Minimal pure-stdlib PDF text extraction (FlateDecode streams,
    Tj/TJ operators). Works for typical simple PDFs; returns "" when
    the PDF uses embedded fonts/encodings this cannot decode — the
    caller must say so instead of silently showing nothing."""
    texts = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        raw = m.group(1)
        try:
            raw = zlib.decompress(raw)
        except zlib.error:
            pass
        # Literal strings in Tj / TJ arrays.
        for sm in re.finditer(rb"\((?:[^()\\]|\\.)*\)\s*Tj", raw):
            s = sm.group(0)
            inner = re.search(rb"\((.*)\)\s*Tj", s, re.S).group(1)
            texts.append(_pdf_string(inner))
        for sm in re.finditer(rb"\[(?:[^\[\]\\]|\\.)*\]\s*TJ", raw):
            parts = re.findall(rb"\((?:[^()\\]|\\.)*\)", sm.group(0))
            texts.append(" ".join(_pdf_string(p[1:-1]) for p in parts))
    return "\n".join(t for t in texts if t.strip())


def _pdf_string(b):
    s = b.decode("latin-1")
    s = s.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
    return s
