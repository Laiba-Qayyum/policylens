import re

from src.ingestion import Chunk


def cited_sources(reply: str, chunks: list[Chunk]) -> tuple[list[Chunk], list[int]]:
    """Return the chunks the reply cites like [1], and any cited numbers that don't exist."""
    numbers = {int(n) for n in re.findall(r"\[(\d+)\]", reply)}
    cited = [chunk for n, chunk in enumerate(chunks, start=1) if n in numbers]
    invalid = sorted(n for n in numbers if n < 1 or n > len(chunks))
    return cited, invalid
