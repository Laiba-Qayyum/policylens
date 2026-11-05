from datetime import date

from fastapi.testclient import TestClient

from src.activity import ActivityLog
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
        words = query.lower().split()
        return [c for c in self.chunks if any(w in c.text.lower() for w in words)][:k]


class FakeLLM:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    def complete(self, prompt: str) -> str:
        return self.reply


def make_client(reply: str = "20 days [1]", api_keys=None) -> TestClient:
    stores = TenantStores(FakeStore)
    chunk = Chunk("annual leave is 20 days", "hr.txt", 1, "policy", "1.0", date(2026, 1, 1))
    stores.add("acme", [chunk])
    app = create_app(stores, FakeLLM(reply), api_keys=api_keys, activity=ActivityLog())
    return TestClient(app)


def activity(client: TestClient, tenant: str = "acme", headers=None) -> dict:
    return client.get(f"/tenants/{tenant}/activity", headers=headers).json()


def test_a_verified_answer_is_logged_and_counted():
    client = make_client()
    client.post("/tenants/acme/ask", json={"question": "annual leave"})

    body = activity(client)

    assert [(e["kind"], e["verified"]) for e in body["events"]] == [("question", True)]
    assert body["summary"] == {"uploads": 0, "questions": 1, "verified_questions": 1}


def test_an_answer_without_a_citation_is_logged_as_not_verified():
    client = make_client("20 days")
    client.post("/tenants/acme/ask", json={"question": "annual leave"})

    assert activity(client)["summary"]["verified_questions"] == 0
    assert activity(client)["summary"]["questions"] == 1


def test_a_refusal_is_logged_but_not_counted_as_verified():
    client = make_client()
    client.post("/tenants/acme/ask", json={"question": "something unrelated"})

    summary = activity(client)["summary"]

    assert summary["questions"] == 1
    assert summary["verified_questions"] == 0


def test_the_question_text_is_never_stored():
    client = make_client()
    client.post("/tenants/acme/ask", json={"question": "my private question about annual leave"})

    response = client.get("/tenants/acme/activity")

    assert "private" not in response.text


def test_each_uploaded_file_is_logged():
    client = make_client()
    client.post(
        "/tenants/acme/documents",
        files=[
            ("files", ("a.txt", b"annual leave is 20 days", "text/plain")),
            ("files", ("b.txt", b"sick leave is 5 days", "text/plain")),
        ],
    )

    events = activity(client)["events"]

    assert sorted(e["detail"] for e in events) == ["a.txt", "b.txt"]
    assert {e["kind"] for e in events} == {"upload"}


def test_a_rejected_upload_is_not_logged():
    client = make_client()
    response = client.post(
        "/tenants/acme/documents",
        files=[("files", ("b.exe", b"not a document", "application/octet-stream"))],
    )

    assert response.status_code == 400
    assert activity(client)["events"] == []


def test_activity_needs_the_key_and_stays_with_its_tenant():
    client = make_client(api_keys=KEYS)

    assert client.get("/tenants/acme/activity").status_code == 401
    assert (
        client.get("/tenants/acme/activity", headers={"X-API-Key": "secret-a"}).status_code == 200
    )
    assert (
        client.get("/tenants/beta/activity", headers={"X-API-Key": "secret-a"}).status_code == 401
    )
