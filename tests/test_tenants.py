from datetime import date

from src.ingestion import Chunk
from src.tenants import TenantStores


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3) -> list[Chunk]:
        words = query.lower().split()
        hits = [c for c in self.chunks if any(w in c.text.lower() for w in words)]
        return hits[:k]


def make_chunk(text: str) -> Chunk:
    return Chunk(text, "doc.txt", 1, "policy", "1.0", date(2026, 1, 1))


def test_tenant_cannot_see_another_tenants_chunks() -> None:
    stores = TenantStores(FakeStore)
    stores.add("acme", [make_chunk("acme leave policy")])
    stores.add("globex", [make_chunk("globex salary policy")])

    results = stores.search("acme", "policy")

    assert [c.text for c in results] == ["acme leave policy"]


def test_unknown_tenant_gets_no_results() -> None:
    assert TenantStores(FakeStore).search("nobody", "policy") == []
