from typing import Protocol

from src.ingestion import Chunk


class VectorStore(Protocol):
    def add(self, chunks: list[Chunk]) -> None: ...

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]: ...
