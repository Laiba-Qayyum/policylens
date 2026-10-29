from datetime import date

from src.conflicts import find_competing_sources
from src.ingestion import Chunk


def make_chunk(source: str, doc_type: str, day: date) -> Chunk:
    return Chunk("some text", source, 1, doc_type, "1.0", day)


def test_two_files_of_same_type_with_different_dates_compete_newest_first() -> None:
    chunks = [
        make_chunk("returns_2025.txt", "policy", date(2025, 1, 1)),
        make_chunk("returns_2026.txt", "policy", date(2026, 1, 1)),
    ]

    assert find_competing_sources(chunks) == ["returns_2026.txt", "returns_2025.txt"]


def test_chunks_from_one_file_do_not_compete() -> None:
    chunks = [
        make_chunk("hr.txt", "policy", date(2026, 1, 1)),
        make_chunk("hr.txt", "policy", date(2026, 1, 1)),
    ]

    assert find_competing_sources(chunks) == []


def test_different_document_types_do_not_compete() -> None:
    chunks = [
        make_chunk("hr.txt", "policy", date(2025, 1, 1)),
        make_chunk("notice.txt", "circular", date(2026, 1, 1)),
    ]

    assert find_competing_sources(chunks) == []
