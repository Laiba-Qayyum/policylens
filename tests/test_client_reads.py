import httpx
import pytest

from src.client import ApiError, PolicyLensClient


def make_client(handler, api_key=None) -> PolicyLensClient:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return PolicyLensClient("http://test", http, api_key=api_key)


def test_documents_gets_the_file_list():
    body = {"documents": [{"source": "a.pdf", "chunks": 2}], "total_chunks": 2}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/tenants/acme/documents"
        return httpx.Response(200, json=body)

    assert make_client(handler).documents("acme") == body


def test_activity_gets_the_events_and_summary():
    body = {"events": [], "summary": {"uploads": 0, "questions": 0, "verified_questions": 0}}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/tenants/acme/activity"
        return httpx.Response(200, json=body)

    assert make_client(handler).activity("acme") == body


def test_reads_send_the_api_key():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers["x-api-key"])
        return httpx.Response(200, json={})

    client = make_client(handler, api_key="secret-a")
    client.documents("acme")
    client.activity("acme")

    assert seen == ["secret-a", "secret-a"]


def test_a_rejected_key_becomes_an_api_error_with_the_server_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Invalid or missing API key"})

    with pytest.raises(ApiError, match="Invalid or missing API key"):
        make_client(handler).documents("acme")


def test_an_unreachable_server_becomes_an_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    with pytest.raises(ApiError, match="Cannot reach"):
        make_client(handler).activity("acme")
