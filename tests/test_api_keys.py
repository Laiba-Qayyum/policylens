from datetime import date

from fastapi.testclient import TestClient

from src.api import create_app
from src.ingestion import Chunk

CHUNK = Chunk("returns within 15 days", "returns.txt", 1, "policy", "1.0", date(2026, 1, 1))
KEYS = {"acme": "secret-a", "beta": "secret-b"}
QUESTION = {"question": "How many days?"}


class FakeStores:
    def add(self, tenant_id, chunks):
        pass

    def search(self, tenant_id, query, k=3, min_score=-1.0):
        return [CHUNK]


class FakeLLM:
    def complete(self, prompt: str) -> str:
        return "15 days [1]"


def make_client(api_keys=KEYS) -> TestClient:
    return TestClient(create_app(FakeStores(), FakeLLM(), api_keys=api_keys))


def key(value: str) -> dict[str, str]:
    return {"X-API-Key": value}


def test_the_right_key_is_accepted():
    response = make_client().post("/tenants/acme/ask", json=QUESTION, headers=key("secret-a"))

    assert response.status_code == 200


def test_a_missing_key_is_rejected():
    assert make_client().post("/tenants/acme/ask", json=QUESTION).status_code == 401


def test_a_wrong_key_is_rejected():
    response = make_client().post("/tenants/acme/ask", json=QUESTION, headers=key("nope"))

    assert response.status_code == 401


def test_one_tenants_key_does_not_open_another_tenant():
    response = make_client().post("/tenants/beta/ask", json=QUESTION, headers=key("secret-a"))

    assert response.status_code == 401


def test_an_unknown_tenant_gets_the_same_answer_as_a_wrong_key():
    client = make_client()

    wrong = client.post("/tenants/acme/ask", json=QUESTION, headers=key("nope"))
    ghost = client.post("/tenants/ghost/ask", json=QUESTION, headers=key("secret-a"))

    assert ghost.status_code == wrong.status_code == 401
    assert ghost.json() == wrong.json()


def test_uploading_needs_the_key_too():
    client = make_client()
    files = {"files": ("a.txt", b"hello", "text/plain")}

    assert client.post("/tenants/acme/documents", files=files).status_code == 401
    ok = client.post("/tenants/acme/documents", files=files, headers=key("secret-a"))
    assert ok.status_code == 200


def test_without_configured_keys_nothing_is_checked():
    response = make_client(api_keys=None).post("/tenants/acme/ask", json=QUESTION)

    assert response.status_code == 200


def test_a_key_with_non_ascii_characters_is_rejected_not_a_server_error():
    headers = {"X-API-Key": "séc".encode()}

    response = make_client().post("/tenants/acme/ask", json=QUESTION, headers=headers)

    assert response.status_code == 401
