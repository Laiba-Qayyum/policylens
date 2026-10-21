from dataclasses import dataclass
from datetime import date
from pathlib import Path

from src.chunking import chunk_text
from src.loaders import load_file


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    page: int
    doc_type: str
    version: str
    doc_date: date


def make_chunks(
    path: Path,
    doc_type: str,
    version: str,
    doc_date: date,
    size: int = 200,
    overlap: int = 40,
) -> list[Chunk]:
    return [
        Chunk(piece, path.name, page, doc_type, version, doc_date)
        for page, text in load_file(path)
        for piece in chunk_text(text, size, overlap)
    ]
