import json

import httpx
import pytest

from src.client import ApiError, PolicyLensClient


def make_client(handler) -> PolicyLensClient:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return PolicyLensClient("http://test", http)


def test_ask_posts_the_question_and_returns_the_answer():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/tenants/acme/ask"
        assert json.loads(request.content) == {"question": "How long?"}
        body = {"answer": "15 days [1]", "sources": [], "competing": [], "verified": True}
        return httpx.Response(200, json=body)

    assert make_client(handler).ask("acme", "How long?")["answer"] == "15 days [1]"


def test_upload_sends_the_files_as_multipart():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/tenants/acme/documents"
        assert request.headers["content-type"].startswith("multipart/form-data")
        assert b'filename="a.txt"' in request.content
        return httpx.Response(200, json={"files": ["a.txt"], "chunks": 1})

    result = make_client(handler).upload("acme", [("a.txt", b"hello")])

    assert result == {"files": ["a.txt"], "chunks": 1}


def test_an_error_response_becomes_an_api_error_with_the_server_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"detail": "Unsupported file type: .exe"})

    with pytest.raises(ApiError, match="Unsupported file type"):
        make_client(handler).upload("acme", [("a.exe", b"x")])


def test_an_unreachable_server_becomes_an_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    with pytest.raises(ApiError, match="Cannot reach"):
        make_client(handler).ask("acme", "How long?")
