def chunk_text(text: str, size: int = 200, overlap: int = 40) -> list[str]:
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    words = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start : start + size]))
        if start + size >= len(words):
            break
    return chunks
