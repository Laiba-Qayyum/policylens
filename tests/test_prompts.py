from datetime import date

from src.ingestion import Chunk
from src.prompts import build_prompt


def make_chunk(
    text: str, source: str = "policy.pdf", page: int = 2, day: date = date(2026, 1, 1)
) -> Chunk:
    return Chunk(text, source, page, "policy", "1.0", day)


def test_prompt_numbers_each_source_with_file_and_page() -> None:
    chunks = [make_chunk("20 days of leave"), make_chunk("Remote work allowed", "hr.docx", 1)]

    prompt = build_prompt("How many leave days?", chunks)

    assert "[1] policy.pdf, page 2: 20 days of leave" in prompt
    assert "[2] hr.docx, page 1: Remote work allowed" in prompt


def test_prompt_contains_question_and_refusal_rule() -> None:
    prompt = build_prompt("How many leave days?", [make_chunk("20 days of leave")])

    assert "Question: How many leave days?" in prompt
    assert "I don't know" in prompt


def test_prompt_shows_version_and_date() -> None:
    prompt = build_prompt("How many leave days?", [make_chunk("20 days of leave")])

    assert "(version 1.0, dated 2026-01-01)" in prompt


def test_prompt_mentions_newest_only_when_sources_compete() -> None:
    one_file = build_prompt("q", [make_chunk("a"), make_chunk("b")])
    two_files = build_prompt("q", [make_chunk("a", "old.txt"), make_chunk("b", "new.txt")])

    assert "newest" not in one_file
    assert "newest" in two_files


def test_prompt_labels_the_newest_source_when_sources_compete() -> None:
    old = make_chunk("30 days", "old.txt", day=date(2025, 1, 1))
    new = make_chunk("15 days", "new.txt", day=date(2026, 1, 1))

    prompt = build_prompt("q", [old, new])

    assert "15 days (version 1.0, dated 2026-01-01, newest)" in prompt
    assert "30 days (version 1.0, dated 2025-01-01)" in prompt


def test_prompt_has_no_newest_label_for_a_single_file() -> None:
    prompt = build_prompt("q", [make_chunk("a"), make_chunk("b")])

    assert "newest)" not in prompt
