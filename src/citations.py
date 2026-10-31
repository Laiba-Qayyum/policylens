import re

from src.ingestion import Chunk


def cited_sources(reply: str, chunks: list[Chunk]) -> tuple[list[Chunk], list[int]]:
    numbers = {int(n) for n in re.findall(r"\[(\d+)\]", reply)}
    cited = [chunk for n, chunk in enumerate(chunks, start=1) if n in numbers]
    invalid = sorted(n for n in numbers if n < 1 or n > len(chunks))
    return cited, invalid


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{4,}|\d{2,}", text.lower()))


def best_support(reply: str, chunks: list[Chunk]) -> Chunk | None:
    """The chunk that shares the most words with the reply, or None if none are shared.

    A word-overlap guess, not proof that the chunk supports the answer.
    """
    reply_words = _words(re.sub(r"\[\d+\]", "", reply))
    best, best_score = None, 0
    for chunk in chunks:
        score = len(reply_words & _words(chunk.text))
        if score > best_score:
            best, best_score = chunk, score
    return best
