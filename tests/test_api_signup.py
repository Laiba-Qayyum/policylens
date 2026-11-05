import logging
from datetime import date

from fastapi.testclient import TestClient

from src.api import create_app
from src.ingestion import Chunk
from src.registry import TenantRegistry
from src.tenants import TenantStores

WRONG = "wrong-secret-value-1234"


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


def make_client(api_keys=None, stores=None) -> TestClient:
    stores = stores or TenantStores(FakeStore)
    app = create_app(stores, FakeLLM(), api_keys=api_keys, registry=TenantRegistry())
    return TestClient(app)


def sign_up(client: TestClient, name: str = "acme"):
    return client.post("/tenants", json={"name": name})


def key(value: str) -> dict[str, str]:
    return {"X-API-Key": value}


def test_creating_a_workspace_returns_its_name_and_key():
    response = sign_up(make_client())

    assert response.status_code == 200
    assert response.json()["tenant"] == "acme"
    assert len(response.json()["api_key"]) >= 16


def test_the_response_with_the_key_must_not_be_cached():
    response = sign_up(make_client())

    assert response.headers["cache-control"] == "no-store"


def test_the_new_key_opens_only_its_own_workspace():
    client = make_client()
    acme_key = sign_up(client, "acme").json()["api_key"]
    sign_up(client, "globex")

    assert client.get("/tenants/acme/documents", headers=key(acme_key)).status_code == 200
    assert client.get("/tenants/globex/documents", headers=key(acme_key)).status_code == 401
    assert client.get("/tenants/acme/documents").status_code == 401


def test_one_workspaces_key_cannot_read_another_workspaces_activity():
    client = make_client()
    acme_key = sign_up(client, "acme").json()["api_key"]
    sign_up(client, "globex")

    assert client.get("/tenants/globex/activity", headers=key(acme_key)).status_code == 401


def test_one_workspaces_key_cannot_upload_to_or_ask_another_workspace():
    client = make_client()
    acme_key = sign_up(client, "acme").json()["api_key"]
    sign_up(client, "globex")
    upload = {"files": ("a.txt", b"hello", "text/plain")}

    uploaded = client.post("/tenants/globex/documents", files=upload, headers=key(acme_key))
    asked = client.post("/tenants/globex/ask", json={"question": "anything"}, headers=key(acme_key))

    assert uploaded.status_code == 401
    assert asked.status_code == 401


def test_a_name_that_is_already_taken_gets_409():
    client = make_client()
    sign_up(client)

    response = sign_up(client)

    assert response.status_code == 409
    assert "already" in response.json()["detail"]


def test_a_name_used_by_a_configured_key_is_taken():
    client = make_client(api_keys={"acme": "configured-key-123456"})

    assert sign_up(client, "acme").status_code == 409


def test_a_name_that_already_has_documents_is_taken():
    stores = TenantStores(FakeStore)
    stores.add("legacy", [Chunk("x", "a.txt", 1, "policy", "1.0", date(2026, 1, 1))])

    assert sign_up(make_client(stores=stores), "legacy").status_code == 409


def test_an_invalid_name_gets_400():
    client = make_client()

    for name in ["Acme", "../evil", ""]:
        assert sign_up(client, name).status_code == 400


def test_configured_keys_still_work_next_to_the_registry():
    client = make_client(api_keys={"acme": "configured-key-123456"})

    response = client.get("/tenants/acme/documents", headers=key("configured-key-123456"))

    assert response.status_code == 200


def test_creating_a_workspace_needs_a_name():
    assert make_client().post("/tenants", json={}).status_code == 422


def test_error_responses_never_contain_a_key():
    client = make_client()
    acme_key = sign_up(client, "acme").json()["api_key"]

    responses = [
        client.get("/tenants/acme/documents", headers=key(WRONG)),
        client.get("/tenants/ghost/documents", headers=key(acme_key)),
        sign_up(client, "acme"),
        sign_up(client, "../evil"),
    ]

    for response in responses:
        assert WRONG not in response.text
        assert acme_key not in response.text


def test_keys_are_never_written_to_the_logs(caplog):
    caplog.set_level(logging.DEBUG)
    client = make_client()
    created = sign_up(client).json()["api_key"]

    client.get("/tenants/acme/documents", headers=key(created))
    client.get("/tenants/acme/documents", headers=key(WRONG))

    assert created not in caplog.text
    assert WRONG not in caplog.text
