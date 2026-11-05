import httpx

from src.client import PolicyLensClient


def make_client(seen: dict, api_key: str | None) -> PolicyLensClient:
    def handler(request: httpx.Request) -> httpx.Response:
        seen["key"] = request.headers.get("x-api-key")
        return httpx.Response(200, json={"answer": "ok"})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    return PolicyLensClient("http://test", http, api_key=api_key)


def test_sends_the_api_key_header_when_one_is_given():
    seen: dict = {}

    make_client(seen, "secret-key").ask("acme", "How long?")

    assert seen["key"] == "secret-key"


def test_sends_no_key_header_when_none_is_given():
    seen: dict = {}

    make_client(seen, None).ask("acme", "How long?")

    assert seen["key"] is None


def test_a_key_with_non_ascii_characters_does_not_crash_the_client():
    seen: dict = {}

    make_client(seen, "séc").ask("acme", "How long?")

    assert seen["key"] is not None
