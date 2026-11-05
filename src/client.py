from urllib.parse import quote

import httpx


class ApiError(Exception):
    """The API could not be reached, or it answered with an error."""


def _detail(response: httpx.Response) -> str:
    try:
        return str(response.json()["detail"])
    except (ValueError, KeyError, TypeError):
        return response.text or f"The API answered with status {response.status_code}"


class PolicyLensClient:
    def __init__(
        self, base_url: str, http: httpx.Client | None = None, api_key: str | None = None
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._http = http or httpx.Client(timeout=120)
        self._headers = {"X-API-Key": api_key.encode()} if api_key else {}

    def create_workspace(self, name: str) -> dict:
        return self._send("POST", f"{self._base_url}/tenants", {}, json={"name": name})

    def upload(self, tenant: str, files: list[tuple[str, bytes]]) -> dict:
        return self._request("POST", tenant, "documents", files=[("files", f) for f in files])

    def ask(self, tenant: str, question: str) -> dict:
        return self._request("POST", tenant, "ask", json={"question": question})

    def documents(self, tenant: str) -> dict:
        return self._request("GET", tenant, "documents")

    def activity(self, tenant: str) -> dict:
        return self._request("GET", tenant, "activity")

    def _request(self, method: str, tenant: str, action: str, **kwargs) -> dict:
        url = f"{self._base_url}/tenants/{quote(tenant, safe='')}/{action}"
        return self._send(method, url, self._headers, **kwargs)

    def _send(self, method: str, url: str, headers: dict, **kwargs) -> dict:
        try:
            response = self._http.request(method, url, headers=headers, **kwargs)
        except httpx.HTTPError as error:
            raise ApiError(f"Cannot reach the API at {self._base_url}") from error
        if response.status_code >= 400:
            raise ApiError(_detail(response))
        return response.json()
