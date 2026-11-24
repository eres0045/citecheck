# CiteCheck — PRASUNEX Innovathon 2026, Round 3 submission notes

Team Fortec (solo) — Ronit Shrimankar. Theme: AI/ML.
Demo video: 40-second screen recording of the live app
(`demo-video/citecheck-demo.mp4` in this repo; a YouTube link will be
added if the submission form asks for one).
Repository: https://github.com/eres0045/citecheck

## What it is

CiteCheck is a study copilot that answers only from the student's own
uploaded notes. Every answer must quote the exact source passage it came
from — or the system says plainly "not in your notes" and refuses to
guess. From the same passages it generates short quizzes, and flags notes
that cite old dates so they can be checked before the exam.

## How to run

```bash
pip install -r requirements.txt
python3 app.py        # http://127.0.0.1:5000
python3 -m pytest tests/ -q   # 8 tests, all passing
```

Pure Python standard library core (`citecheck.py`) + Flask app (`app.py`).
No paid LLM, no API keys, runs offline. Demo notes are synthetic and
labelled as such (`sample_notes.md`).

## Implemented features

1. **Upload notes** — `.txt`, `.md`, or simple `.pdf` (stdlib FlateDecode
   extractor). Scanned-image PDFs return a clear error instead of empty
   text. Notes are chunked into passages, each keeping its source file and
   chunk id for citations.
2. **Citation-enforced answers** — a question retrieves the best passages
   from the student's notes only and answers by quoting them, with
   `[source · chunk N]` citations. If no passage supports the question
   (best score below threshold), it refuses instead of guessing.
3. **Quiz generation** — 5 questions drawn from the notes; every question
   blanks one key term, options are that term plus 3 distractors from the
   notes, and every item carries its citation.
4. **Stale check** — flags any chunk citing a pre-2024 date (e.g. the
   sample's 2019-syllabus note) so the student verifies it against the
   current syllabus.

Verified live 24 Nov 2026: 8/8 tests green; every endpoint exercised on
the running app (cited answer, deliberate refusal, quiz, stale flag, PDF
upload, and all empty-state errors). Full check saved in
`VERIFICATION.md`.

## Limitations (stated honestly)

- Retrieval is **TF-IDF (stdlib)**, not the TensorFlow embeddings the
  Round 2 design promised. The swap-in point is `retrieve()` in
  `citecheck.py`; TensorFlow is not installed on the demo machine and the
  prototype must run offline.
- Frontend is a Flask server-rendered page, not the React + Tailwind UI
  from the Round 2 design.
- No persistent vector store — the index is an in-memory list, one user
  at a time, per process.
- Chunks keep source + chunk id but **not page numbers** for PDFs.
- Stale detection is **date-based (pre-2024) only**; it does not yet flag
  quiz items that lost source support, and quiz generation can draw a
  question from a stale chunk.

## Future development plans

- Swap TF-IDF for TensorFlow embeddings at `retrieve()` (interface is
  already a single function) and a persistent per-student local index.
- React + Tailwind frontend; multi-user accounts with per-student indexes.
- Track PDF page numbers in chunks so citations point at the exact page.
- Stale flags based on source support (a quiz item whose passage was
  edited away gets flagged), plus syllabus-version awareness.
- Measure on real student notes: answer accuracy, refusal calibration,
  and quiz quality — no metrics are claimed yet.
