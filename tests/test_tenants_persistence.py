from datetime import date

import pytest

from src.ingestion import Chunk
from src.tenants import TenantStores


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]:
        return self.chunks[:k]


def make(text: str) -> Chunk:
    return Chunk(text, "doc.pdf", 1, "policy", "1.0", date(2026, 1, 1))


def test_chunks_survive_a_restart(tmp_path):
    first = TenantStores(FakeStore, directory=tmp_path)
    first.add("acme", [make("returns within 15 days")])

    second = TenantStores(FakeStore, directory=tmp_path)

    assert second.search("acme", "returns") == [make("returns within 15 days")]


def test_adding_twice_keeps_both_after_a_restart(tmp_path):
    first = TenantStores(FakeStore, directory=tmp_path)
    first.add("acme", [make("one")])
    first.add("acme", [make("two")])

    second = TenantStores(FakeStore, directory=tmp_path)

    assert second.search("acme", "x") == [make("one"), make("two")]


def test_tenants_stay_separate_after_a_restart(tmp_path):
    first = TenantStores(FakeStore, directory=tmp_path)
    first.add("acme", [make("acme rule")])
    first.add("beta", [make("beta rule")])

    second = TenantStores(FakeStore, directory=tmp_path)

    assert second.search("acme", "x") == [make("acme rule")]
    assert second.search("beta", "x") == [make("beta rule")]


def test_unsafe_tenant_id_is_rejected_and_writes_nothing(tmp_path):
    stores = TenantStores(FakeStore, directory=tmp_path)

    with pytest.raises(ValueError):
        stores.add("../evil", [make("x")])

    assert list(tmp_path.iterdir()) == []
