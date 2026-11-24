# CiteCheck — Round 3 full criteria verification (SAVED)

**Verified by Muse, live, Tue 24 Nov 2026 ~08:46–08:55 IST.**
Method: read all source files, re-ran the test suite twice, and exercised the
running Flask app end-to-end with curl (every endpoint, plus a hand-built real
PDF and a blank/image PDF). Official Round 3 requirements taken from the
Unstop event page (unstop.com/hackathons/prasunex-innovathon-2026-prasunex-1772904).
R1/R2 promises taken from the submitted decks in
`~/workspace/goals/hackathon-registration-drive/files/`
(`PRASUNEX_R1_CiteCheck_draft.md`, `PRASUNEX_R2_CiteCheck.pptx` — 10 slides).

## 1. Test suite — PASS

`~/workspace/.venvs/neo4j/bin/python -m pytest tests/ -q` → **8 passed**
(0.03s). Re-run after the fixes in §5 → **8 passed** again (0.02s).
System python3 has no pytest/Flask — the venv above is the working runner.

## 2. Live app — PASS (all endpoints hit by me just now)

Server: Flask on http://127.0.0.1:5000 (running, debug mode).

| Check | Observed |
|---|---|
| GET / | 200, page loads |
| Upload sample notes | 9 chunks loaded |
| Ask "Where does photosynthesis take place?" | Answered, quoted, citations [sample_notes.md (SYNTHETIC) · chunk 2, chunk 4], score 0.444 |
| Ask "What is the capital of France?" | REFUSED, "Not in your notes — I can't cite this, so I won't answer it.", citations [], score 0.0 |
| Make quiz | 5 questions, each 4 options, answer always in options, every item cited |
| Stale check | 1 flag — chunk 9, years 2019 + 2021 |
| Upload real FlateDecode PDF | 1 chunk; ask on it answered with citation |
| Upload blank / image-only PDF | Clean 400 error: "Could not read text from that PDF (scanned image or unsupported encoding). Try a .txt or .md export instead." |
| Upload .txt notes | 2 chunks |
| Empty question | 400 "Ask a question first." |
| Ask / quiz / stale with no notes loaded | 400 "Upload notes first." (each) |
| Upload with no file | 400 "No file uploaded." |

## 3. Official Round 3 required submissions — status

| Required submission (Unstop) | Status |
|---|---|
| Working prototype / MVP / proof of concept | DONE — Flask app, all 4 loops live (see §2) |
| Live demonstration or demonstration video, as instructed | NOT DONE — no video recorded yet; live demo possible via the app |
| Source code or repository link, where applicable | NOT DONE — code is local only, no public GitHub repo yet |
| Brief technical documentation | PARTIAL — README.md exists with run instructions + honest limits; no standalone technical doc for the submission form yet |
| Explanation of implemented features and limitations | PARTIAL — README lists honest limits; must be written into the submission |
| Future development plans and potential improvements | NOT DONE — R2 deck slide 10 has "what's next"; needs writing up |

## 4. Official Round 3 evaluation criteria — status

| Criterion | Verdict |
|---|---|
| Functionality and implementation quality | STRONG — all 4 features work live, verified above |
| Technical execution | WEAKENED — retrieval is TF-IDF, not the TensorFlow embeddings the R2 deck promised; no React frontend (Flask templates); no persistent vector store (in-memory list) |
| User experience and usability | OK — simple 3-section UI, works; plain styling, no polish |
| Innovation and effectiveness | STRONG — hard citation gate + deliberate refusal is the core idea and it works |
| Practical applicability and scalability | WEAKENED — single-user, in-memory, one session at a time; local-first claim holds for the demo only |
| Quality of the demonstration | BLOCKED — no video yet; the demo script had wrong numbers (fixed, §5) |

## 5. Issues found and FIXED during this check

1. **README demo script was wrong**: said "5 chunks loaded" — real count is **9**.
   Fixed to 9.
2. **README demo script citation was wrong**: said `[sample_notes.md · chunk 1]` —
   the live answer cites **chunk 2 and chunk 4**. Fixed.
3. **Quiz showed "ronit" as an answer option**: the sample file's header line
   ("not Ronit's real notes") tokenized into the distractor pool. Fixed in
   `citecheck.py` — the pool now excludes heading chunks. Re-verified live:
   5 questions, no "ronit" in any option, all answers in options, all cited.
   Tests still 8/8 after the fix.

## 6. Gaps vs what Rounds 1–2 promised (must be stated honestly in the submission)

- **TensorFlow embeddings → TF-IDF (stdlib).** R2 slide 4/5 promised TF
  embeddings + local vector store. Swap-in point is `retrieve()` in
  `citecheck.py`; TF is not installed here and the prototype must run offline.
  Do NOT claim TF embeddings in the demo or submission.
- **React + Tailwind frontend → Flask server-rendered template.** Works, simpler.
- **Local vector store, one index per student → in-memory list**, no persistence,
  one user at a time.
- **Chunks keep source + chunk id, but NOT page numbers** (R2 promised "source +
  page kept"). PDF page numbers are not tracked.
- **Stale flag is date-based (pre-2024) only.** R1 promised quiz items losing
  source support get flagged; the prototype flags old dates instead. Different,
  weaker — say so in the submission.
- **Quiz can draw questions from stale chunks** (e.g. the 2019-syllabus chunk
  produced a quiz question). No stale filtering in quiz generation.

## 7. Still needed before submitting (deadline Tue 25 Nov 23:00 IST)

1. **Demo video (< 3 min)** — record on the live app using the corrected
   5-step script in README.md. Notes decision: Ronit has not answered own
   notes vs synthetic sample; the bundled sample is labelled SYNTHETIC and
   works as-is, so the submission defaults to the sample unless he says
   otherwise.
2. **Public GitHub repo** — create, push code + README, use as the repo link.
3. **Submission write-up** — brief technical doc + features/limitations
   (from §6) + future plans.
4. **Unstop dashboard format check** — the page says "as instructed"; the exact
   fields/file types live in his Unstop dashboard (sign-in as 1@gmail needed).
   Nothing is submitted without his go-ahead + the pre-submit check.
