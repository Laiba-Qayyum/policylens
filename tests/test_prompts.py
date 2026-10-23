from datetime import date

from src.ingestion import Chunk
from src.prompts import build_prompt


def make_chunk(text: str, source: str = "policy.pdf", page: int = 2) -> Chunk:
    return Chunk(text, source, page, "policy", "1.0", date(2026, 1, 1))


def test_prompt_numbers_each_source_with_file_and_page() -> None:
    chunks = [make_chunk("20 days of leave"), make_chunk("Remote work allowed", "hr.docx", 1)]

    prompt = build_prompt("How many leave days?", chunks)

    assert "[1] policy.pdf, page 2: 20 days of leave" in prompt
    assert "[2] hr.docx, page 1: Remote work allowed" in prompt


def test_prompt_contains_question_and_refusal_rule() -> None:
    prompt = build_prompt("How many leave days?", [make_chunk("20 days of leave")])

    assert "Question: How many leave days?" in prompt
    assert "I don't know" in prompt
