from pathlib import Path

from docx import Document

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

    raise ValueError(f"Unsupported file type: {path.suffix or 'none'}")
