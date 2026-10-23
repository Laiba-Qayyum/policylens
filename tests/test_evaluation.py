from datetime import date

from src.evaluation import Case, evaluate
from src.ingestion import Chunk


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]:
        words = query.lower().split()
        return [c for c in self.chunks if any(w in c.text.lower() for w in words)][:k]


def test_evaluate_counts_hits_and_correct_refusals() -> None:
    store = FakeStore()
    store.add([Chunk("annual leave is 20 days", "doc.txt", 1, "policy", "1.0", date(2026, 1, 1))])
    cases = [
        Case("annual leave", "20 days"),  # found: correct
        Case("parking", None),  # nothing retrieved: correct refusal
        Case("leave", "30 days"),  # retrieved text lacks the phrase: wrong
    ]

    assert evaluate(store, cases) == (2, 3)
