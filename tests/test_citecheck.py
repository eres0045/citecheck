"""Tests for CiteCheck core. Run: python3 -m pytest tests/ -q"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from citecheck import (  # noqa: E402
    answer,
    chunk_text,
    extract_pdf_text,
    make_quiz,
    retrieve,
    stale_flags,
)

NOTES = """
Photosynthesis is the process by which green plants convert sunlight,
water and carbon dioxide into glucose and oxygen. It takes place in the
chloroplasts of the leaves.

Cellular respiration releases energy from glucose in the mitochondria.
The three stages are glycolysis, the Krebs cycle and the electron
transport chain.

The light-dependent reactions take place on the thylakoid membranes and
produce ATP and NADPH for the Calvin cycle.

The Calvin cycle fixes carbon dioxide into glucose in the stroma of the
chloroplast, using ATP and NADPH from the light reactions.

Glycolysis breaks glucose into pyruvate in the cytoplasm and produces a
small net gain of ATP without needing oxygen.

In the 2019 syllabus, the Krebs cycle carried 3 marks in the board exam.
"""


def chunks():
    return chunk_text(NOTES, "sample_notes.md")


def test_chunking_keeps_source_and_ids():
    cs = chunks()
    assert len(cs) >= 3
    assert all(c["source"] == "sample_notes.md" for c in cs)
    assert [c["id"] for c in cs] == list(range(1, len(cs) + 1))


def test_answer_quotes_notes_with_citation():
    r = answer("Where does photosynthesis take place?", chunks())
    assert r["answered"] is True
    assert "chloroplast" in r["answer"].lower()
    assert r["citations"], "answered replies must carry a citation"


def test_answer_refuses_when_not_in_notes():
    r = answer("What is the capital of France?", chunks())
    assert r["answered"] is False
    assert r["citations"] == []
    assert "not in your notes" in r["answer"].lower()


def test_retrieve_ranks_relevant_chunk_first():
    top = retrieve("Krebs cycle stages", chunks(), top_k=1)
    assert top and "krebs" in top[0][1]["text"].lower()


def test_quiz_has_five_questions_with_answers_in_options():
    q = make_quiz(chunks(), n=5, seed=7)
    assert len(q) == 5
    for item in q:
        assert item["answer"] in item["options"]
        assert len(item["options"]) == 4
        assert "_____" in item["question"]
        assert item["citation"]["source"] == "sample_notes.md"


def test_quiz_is_deterministic_for_same_seed():
    assert make_quiz(chunks(), seed=7) == make_quiz(chunks(), seed=7)


def test_stale_flags_catch_old_years_only():
    flags = stale_flags(chunks())
    assert len(flags) == 1
    assert flags[0]["years"] == [2019]
    assert "2019" in flags[0]["note"]


def test_empty_notes_refuse_cleanly():
    assert answer("anything?", [])["answered"] is False
    assert retrieve("anything?", []) == []
    assert make_quiz([]) == []
    assert stale_flags([]) == []
