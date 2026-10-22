from datetime import date

import numpy as np

from src.faiss_store import FaissStore
from src.ingestion import Chunk
from src.tenants import TenantStores

VOCAB = ["leave", "salary", "remote", "approval"]


class FakeEmbedder:
    def embed(self, texts: list[str]) -> np.ndarray:
        rows = [[t.lower().count(w) for w in VOCAB] for t in texts]
        vectors = np.array(rows, dtype="float32")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return vectors / norms


def make_store() -> FaissStore:
    return FaissStore(FakeEmbedder(), dim=len(VOCAB))


def make_chunk(text: str) -> Chunk:
    return Chunk(text, "doc.txt", 1, "policy", "1.0", date(2026, 1, 1))


def test_search_returns_closest_chunk_first() -> None:
    store = make_store()
    store.add([make_chunk("annual leave days"), make_chunk("salary paid monthly")])

    assert store.search("leave", k=1)[0].text == "annual leave days"


def test_empty_store_returns_nothing() -> None:
    assert make_store().search("leave") == []


def test_k_larger_than_store_size_is_safe() -> None:
    store = make_store()
    store.add([make_chunk("annual leave days")])

    assert len(store.search("leave", k=5)) == 1


def test_tenants_with_real_faiss_stores_stay_isolated() -> None:
    stores = TenantStores(make_store)
    stores.add("acme", [make_chunk("acme leave policy")])
    stores.add("globex", [make_chunk("globex salary policy")])

    texts = [c.text for c in stores.search("globex", "leave")]

    assert "acme leave policy" not in texts
