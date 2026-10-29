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
    def __init__(self, reply: str = "20 days [1]") -> None:
        self.reply = reply

    def complete(self, prompt: str) -> str:
        return self.reply


def make_client(reply: str = "20 days [1]") -> TestClient:
    stores = TenantStores(FakeStore)
    chunk = Chunk("annual leave is 20 days", "hr.txt", 1, "policy", "1.0", date(2026, 1, 1))
    stores.add("acme", [chunk])
    return TestClient(create_app(stores, FakeLLM(reply)))


def test_ask_returns_answer_sources_and_competing() -> None:
    response = make_client().post("/tenants/acme/ask", json={"question": "annual leave"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "20 days [1]",
        "sources": [{"source": "hr.txt", "page": 1}],
        "competing": [],
        "verified": True,
    }


def test_ask_for_another_tenant_gets_a_refusal_and_no_sources() -> None:
    response = make_client().post("/tenants/globex/ask", json={"question": "annual leave"})

    assert response.json() == {
        "answer": "I don't know.",
        "sources": [],
        "competing": [],
        "verified": True,
    }


def test_ask_requires_a_question() -> None:
    response = make_client().post("/tenants/acme/ask", json={})

    assert response.status_code == 422


def test_ask_flags_an_answer_that_cites_no_source() -> None:
    response = make_client("20 days").post("/tenants/acme/ask", json={"question": "annual leave"})

    assert response.json()["verified"] is False
    assert response.json()["sources"] == [{"source": "hr.txt", "page": 1}]


def make_empty_client() -> tuple[TestClient, TenantStores]:
    stores = TenantStores(FakeStore)
    return TestClient(create_app(stores, FakeLLM())), stores


def test_upload_adds_the_file_to_the_tenant() -> None:
    client, stores = make_empty_client()

    response = client.post(
        "/tenants/acme/documents",
        files=[("files", ("policy.txt", b"annual leave is 20 days", "text/plain"))],
    )

    assert response.status_code == 200
    assert response.json() == {"files": ["policy.txt"], "chunks": 1}
    assert [c.source for c in stores.search("acme", "leave")] == ["policy.txt"]
    assert stores.search("globex", "leave") == []


def test_upload_keeps_only_the_file_name_not_the_folders() -> None:
    client, _ = make_empty_client()

    response = client.post(
        "/tenants/acme/documents",
        files=[("files", ("../../evil.txt", b"annual leave is 20 days", "text/plain"))],
    )

    assert response.json()["files"] == ["evil.txt"]


def test_upload_of_an_unsupported_file_is_rejected_and_adds_nothing() -> None:
    client, stores = make_empty_client()

    response = client.post(
        "/tenants/acme/documents",
        files=[
            ("files", ("a.txt", b"annual leave is 20 days", "text/plain")),
            ("files", ("b.exe", b"not a document", "application/octet-stream")),
        ],
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
    assert stores.search("acme", "leave") == []
