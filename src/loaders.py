from pathlib import Path

from docx import Document
from pypdf import PdfReader

PageText = tuple[int, str]


def load_file(path: Path) -> list[PageText]:
    if not path.is_file():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix == ".txt":
        return [(1, path.read_text(encoding="utf-8-sig"))]
    if suffix == ".docx":
        paragraphs = [p.text for p in Document(str(path)).paragraphs]
        return [(1, "\n".join(paragraphs))]
    if suffix == ".pdf":
        pages = PdfReader(str(path)).pages
        return [(n, page.extract_text()) for n, page in enumerate(pages, start=1)]

    raise ValueError(f"Unsupported file type: {path.suffix or 'none'}")
