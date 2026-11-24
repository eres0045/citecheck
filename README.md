# CiteCheck — PRASUNEX Innovathon 2026, Round 3 prototype

**Status (Mon 23 Nov 2026, 07:00 IST): WORKING prototype, tests green.**
Built this morning because no Round 3 prototype code existed anywhere in
the workspace — only the Round 1/2 decks — and the build window closes
**Tue 25 Nov 2026, 23:00 IST** (final jury Mon 1 Dec, winner ₹51,000 + PPI).

## What it does — the full loop, live in under 3 minutes

1. Upload notes (`.txt` / `.md` / simple `.pdf`) or load the bundled sample.
2. Ask a question → quoted answer with a citation, **or a refusal**
   ("Not in your notes — I can't cite this, so I won't answer it") when
   nothing in the notes supports it. The citation gate is the whole idea.
3. "Make quiz" → 5 questions drawn from the notes, each with 4 options;
   every correct answer is a term from the notes, with its citation.
4. "Check stale notes" → flags anything citing a pre-2024 date
   (e.g. the sample's "2019 syllabus" note) so it can be verified.

## Run it

```bash
pip install -r requirements.txt
python3 app.py        # http://127.0.0.1:5000
python3 -m pytest tests/ -q   # 8 tests
```

## Demo script (jury, < 3 min)

1. Load sample notes → "9 chunks loaded".
2. Ask "Where does photosynthesis take place?" → quoted answer,
   citations `[sample_notes.md (SYNTHETIC) · chunk 2, chunk 4]`.
3. Ask "What is the capital of France?" → refusal, no citation invented.
4. Make quiz → 5 questions, answers shown with citations.
5. Check stale notes → flags the 2019-syllabus chunk.

## Honest limits — do not claim otherwise in the demo

- Retrieval is **TF-IDF (stdlib)**, not the TensorFlow embeddings the
  Round 2 deck promised. TensorFlow is not installed here and the
  prototype must run offline. The swap-in point is `retrieve()` in
  `citecheck.py`; TF embeddings can replace TF-IDF without touching the
  answer / quiz / stale logic.
- PDF reading is a minimal stdlib extractor (FlateDecode streams,
  Tj/TJ). Scanned-image PDFs and unusual encodings return a clear
  error instead of empty text — use a `.txt`/`.md` export for those.
- Stale detection is date-based (pre-2024) only; it does not yet know
  syllabus versions.
- All state is in-memory per process; one user at a time for the demo.

## Still Ronit's call (open since 18 Nov)

Demo on **his own notes or the synthetic sample notes** (labelled as
such)? The sample is bundled so the demo works either way — swap the
file, nothing else changes. If he picks his own notes, upload them and
re-run the 5-step script above before the jury.

## Still to do before Tue 25 Nov 23:00 IST

- [ ] Ronit's notes decision (above)
- [ ] Record the < 3-min demo video on the live app
- [ ] Check the Round 3 submission format on Unstop (Round 2 took one
      PDF; do NOT assume Round 3 takes the same) — needs his Unstop
      sign-in, no submit without his go-ahead + pre-submit check
- [ ] Optional: swap TF-IDF for TensorFlow embeddings if TF is
      installed on the demo machine, and re-run tests
