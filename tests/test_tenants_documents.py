from datetime import date

from src.ingestion import Chunk
from src.tenants import TenantStores


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]:
        return self.chunks[:k]


def make(text: str, source: str) -> Chunk:
    return Chunk(text, source, 1, "policy", "1.0", date(2026, 1, 1))


def test_lists_each_file_with_its_chunk_count():
    stores = TenantStores(FakeStore)
    stores.add("acme", [make("x", "a.pdf"), make("y", "a.pdf"), make("z", "b.pdf")])

    assert stores.documents("acme") == [
        {"source": "a.pdf", "chunks": 2},
        {"source": "b.pdf", "chunks": 1},
    ]


def test_an_unknown_tenant_has_no_documents():
    assert TenantStores(FakeStore).documents("ghost") == []


def test_uploading_a_file_again_replaces_its_chunks():
    stores = TenantStores(FakeStore)
    stores.add("acme", [make("old", "a.pdf")])

    stores.add("acme", [make("new", "a.pdf")])

    assert stores.documents("acme") == [{"source": "a.pdf", "chunks": 1}]
    assert stores.search("acme", "q") == [make("new", "a.pdf")]


def test_replacing_one_file_keeps_the_others():
    stores = TenantStores(FakeStore)
    stores.add("acme", [make("a1", "a.pdf"), make("b1", "b.pdf")])

    stores.add("acme", [make("a2", "a.pdf")])

    assert sorted(d["source"] for d in stores.documents("acme")) == ["a.pdf", "b.pdf"]
    assert make("a1", "a.pdf") not in stores.search("acme", "q", k=10)


def test_a_replacement_survives_a_restart(tmp_path):
    first = TenantStores(FakeStore, directory=tmp_path)
    first.add("acme", [make("old", "a.pdf")])
    first.add("acme", [make("new", "a.pdf")])

    second = TenantStores(FakeStore, directory=tmp_path)

    assert second.search("acme", "q") == [make("new", "a.pdf")]
