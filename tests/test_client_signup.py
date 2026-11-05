import json

import httpx
import pytest

from src.client import ApiError, PolicyLensClient

CREATED = {"tenant": "acme", "api_key": "k" * 32}


def make_client(handler, api_key=None) -> PolicyLensClient:
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return PolicyLensClient("http://test", http, api_key=api_key)


def test_create_workspace_posts_the_name_and_returns_the_key():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/tenants"
        assert json.loads(request.content) == {"name": "acme"}
        return httpx.Response(200, json=CREATED)

    assert make_client(handler).create_workspace("acme") == CREATED


def test_create_workspace_does_not_send_an_existing_key():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append("x-api-key" in request.headers)
        return httpx.Response(200, json=CREATED)

    make_client(handler, api_key="another-workspace-key").create_workspace("acme")

    assert seen == [False]


def test_a_taken_name_becomes_an_api_error_with_the_server_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json={"detail": "That workspace name is already taken"})

    with pytest.raises(ApiError, match="already taken"):
        make_client(handler).create_workspace("acme")


def test_an_unreachable_server_becomes_an_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    with pytest.raises(ApiError, match="Cannot reach"):
        make_client(handler).create_workspace("acme")
