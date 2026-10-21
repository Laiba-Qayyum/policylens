from datetime import date
from pathlib import Path

from src.ingestion import Chunk, make_chunks

DOC_DATE = date(2026, 1, 15)


def test_chunks_carry_metadata(tmp_path: Path):
    file = tmp_path / "returns.txt"
    file.write_text("one two three four five six", encoding="utf-8")
    chunks = make_chunks(file, "circular", "v2", DOC_DATE, size=4, overlap=1)
    assert chunks == [
        Chunk("one two three four", "returns.txt", 1, "circular", "v2", DOC_DATE),
        Chunk("four five six", "returns.txt", 1, "circular", "v2", DOC_DATE),
    ]


def test_empty_file_gives_no_chunks(tmp_path: Path):
    file = tmp_path / "empty.txt"
    file.write_text("", encoding="utf-8")
    assert make_chunks(file, "handbook", "v1", DOC_DATE) == []
