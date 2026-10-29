from datetime import date

from fastapi.testclient import TestClient

from src.api import create_app
from src.ingestion import Chunk
from src.tenants import TenantStores


class FakeStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def search(self, query: str, k: int = 3, min_score: float = -1.0) -> list[Chunk]:
        words = query.lower().split()
        return [c for c in self.chunks if any(w in c.text.lower() for w in words)][:k]


class FakeLLM:
    def complete(self, prompt: str) -> str:
        return "20 days [1]"


def make_client() -> TestClient:
    stores = TenantStores(FakeStore)
    chunk = Chunk("annual leave is 20 days", "hr.txt", 1, "policy", "1.0", date(2026, 1, 1))
    stores.add("acme", [chunk])
    return TestClient(create_app(stores, FakeLLM()))


def test_ask_returns_answer_sources_and_competing() -> None:
    response = make_client().post("/tenants/acme/ask", json={"question": "annual leave"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "20 days [1]",
        "sources": [{"source": "hr.txt", "page": 1}],
        "competing": [],
    }


def test_ask_for_another_tenant_gets_a_refusal_and_no_sources() -> None:
    response = make_client().post("/tenants/globex/ask", json={"question": "annual leave"})

    assert response.json() == {"answer": "I don't know.", "sources": [], "competing": []}


def test_ask_requires_a_question() -> None:
    response = make_client().post("/tenants/acme/ask", json={})

    assert response.status_code == 422
