"""CiteCheck prototype — Flask app (Round 3, PRASUNEX Innovathon 2026).

Run:  pip install -r requirements.txt
       python3 app.py
Then open http://127.0.0.1:5000

Demo loop (under 3 minutes):
  1. Upload notes (.txt / .md / simple .pdf) — or click "Load sample notes".
  2. Ask a question -> quoted answer with citation, or a refusal.
  3. Click "Make quiz" -> 5 questions drawn from the notes.
  4. Stale flags list anything citing a pre-2024 date.

All state is in-memory and per-process; nothing is uploaded anywhere.
"""
import os

from flask import Flask, jsonify, render_template, request

from citecheck import (
    answer,
    chunk_text,
    extract_pdf_text,
    make_quiz,
    stale_flags,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

CHUNKS = []  # in-memory index for this session


def _load_text(filename, data):
    if filename.lower().endswith(".pdf"):
        text = extract_pdf_text(data)
        if not text.strip():
            return None, (
                "Could not read text from that PDF (scanned image or "
                "unsupported encoding). Try a .txt or .md export instead."
            )
        return text, None
    try:
        return data.decode("utf-8"), None
    except UnicodeDecodeError:
        return data.decode("latin-1"), None


@app.route("/")
def index():
    return render_template(
        "index.html",
        loaded=len(CHUNKS),
        sample_available=True,
    )


@app.route("/upload", methods=["POST"])
def upload():
    global CHUNKS
    if "file" in request.files and request.files["file"].filename:
        f = request.files["file"]
        text, err = _load_text(f.filename, f.read())
        if err:
            return jsonify({"ok": False, "error": err}), 400
        CHUNKS = chunk_text(text, f.filename)
    elif request.form.get("sample"):
        path = os.path.join(os.path.dirname(__file__), "sample_notes.md")
        with open(path, encoding="utf-8") as fh:
            CHUNKS = chunk_text(fh.read(), "sample_notes.md (SYNTHETIC)")
    else:
        return jsonify({"ok": False, "error": "No file uploaded."}), 400
    return jsonify({"ok": True, "chunks": len(CHUNKS)})


@app.route("/ask", methods=["POST"])
def ask():
    q = (request.json or {}).get("question", "").strip()
    if not q:
        return jsonify({"ok": False, "error": "Ask a question first."}), 400
    if not CHUNKS:
        return jsonify({"ok": False, "error": "Upload notes first."}), 400
    return jsonify({"ok": True, **answer(q, CHUNKS)})


@app.route("/quiz", methods=["POST"])
def quiz():
    if not CHUNKS:
        return jsonify({"ok": False, "error": "Upload notes first."}), 400
    return jsonify({"ok": True, "questions": make_quiz(CHUNKS)})


@app.route("/stale", methods=["GET"])
def stale():
    if not CHUNKS:
        return jsonify({"ok": False, "error": "Upload notes first."}), 400
    return jsonify({"ok": True, "flags": stale_flags(CHUNKS)})


if __name__ == "__main__":
    app.run(debug=True)
