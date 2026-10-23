from collections.abc import Callable

from src.ingestion import Chunk
from src.vector_store import VectorStore


class TenantStores:
    def __init__(self, store_factory: Callable[[], VectorStore]) -> None:
        self._factory = store_factory
        self._stores: dict[str, VectorStore] = {}

    def add(self, tenant_id: str, chunks: list[Chunk]) -> None:
        if tenant_id not in self._stores:
            self._stores[tenant_id] = self._factory()
        self._stores[tenant_id].add(chunks)

    def search(
        self, tenant_id: str, query: str, k: int = 3, min_score: float = -1.0
    ) -> list[Chunk]:
        store = self._stores.get(tenant_id)
        return store.search(query, k, min_score) if store else []
