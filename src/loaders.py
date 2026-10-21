from pathlib import Path

PageText = tuple[int, str]


def load_file(path: Path) -> list[PageText]:
    if not path.is_file():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".txt":
        return [(1, path.read_text(encoding="utf-8-sig"))]

    raise ValueError(f"Unsupported file type: {path.suffix or 'none'}")
