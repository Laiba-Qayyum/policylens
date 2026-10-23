import faiss

from src.embeddings import Embedder
from src.ingestion import Chunk


class FaissStore:
    def __init__(self, embedder: Embedder, dim: int) -> None:
        self._embedder = embedder
        self._index = faiss.IndexFlatIP(dim)
        self._chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        self._index.add(self._embedder.embed([c.text for c in chunks]))
        self._chunks.extend(chunks)

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]:
        if not self._chunks:
            return []
        query_vector = self._embedder.embed([query])
        scores, ids = self._index.search(query_vector, min(k, len(self._chunks)))
        return [
            self._chunks[i]
            for score, i in zip(scores[0], ids[0], strict=True)
            if score >= min_score
        ]
