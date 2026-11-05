from datetime import date

from fastapi.testclient import TestClient

from src.api import create_app
from src.ingestion import Chunk
from src.tenants import TenantStores

KEYS = {"acme": "secret-a", "beta": "secret-b"}


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]:
        return self.chunks[:k]


class FakeLLM:
    def complete(self, prompt: str) -> str:
        return "ok [1]"


def make(source: str) -> Chunk:
    return Chunk("text", source, 1, "policy", "1.0", date(2026, 1, 1))


def make_client(api_keys=None) -> TestClient:
    stores = TenantStores(FakeStore)
    stores.add("acme", [make("a.pdf"), make("a.pdf"), make("b.pdf")])
    stores.add("beta", [make("secret.pdf")])
    return TestClient(create_app(stores, FakeLLM(), api_keys=api_keys))


def test_lists_files_with_chunk_counts_and_a_total():
    response = make_client().get("/tenants/acme/documents")

    assert response.status_code == 200
    assert response.json() == {
        "documents": [
            {"source": "a.pdf", "chunks": 2},
            {"source": "b.pdf", "chunks": 1},
        ],
        "total_chunks": 3,
    }


def test_a_tenant_with_nothing_uploaded_gets_an_empty_list():
    response = make_client().get("/tenants/ghost/documents")

    assert response.json() == {"documents": [], "total_chunks": 0}


def test_listing_needs_the_key():
    client = make_client(api_keys=KEYS)

    assert client.get("/tenants/acme/documents").status_code == 401
    ok = client.get("/tenants/acme/documents", headers={"X-API-Key": "secret-a"})
    assert ok.status_code == 200


def test_one_tenants_key_cannot_list_another_tenants_files():
    client = make_client(api_keys=KEYS)

    response = client.get("/tenants/beta/documents", headers={"X-API-Key": "secret-a"})

    assert response.status_code == 401
