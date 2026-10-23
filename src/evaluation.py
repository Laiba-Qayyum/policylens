from dataclasses import dataclass

from src.vector_store import VectorStore


@dataclass(frozen=True)
class Case:
    question: str
    expected: str | None  # phrase a retrieved chunk must contain; None = should refuse


def evaluate(
    store: VectorStore, cases: list[Case], k: int = 3, min_score: float = -1.0
) -> tuple[int, int]:
    correct = 0
    for case in cases:
        chunks = store.search(case.question, k, min_score)
        if case.expected is None:
            correct += not chunks
        else:
            correct += any(case.expected in c.text for c in chunks)
    return correct, len(cases)
