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
    def __init__(self, base_url: str, http: httpx.Client | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._http = http or httpx.Client(timeout=120)

    def upload(self, tenant: str, files: list[tuple[str, bytes]]) -> dict:
        return self._post(tenant, "documents", files=[("files", f) for f in files])

    def ask(self, tenant: str, question: str) -> dict:
        return self._post(tenant, "ask", json={"question": question})

    def _post(self, tenant: str, action: str, **kwargs) -> dict:
        url = f"{self._base_url}/tenants/{quote(tenant, safe='')}/{action}"
        try:
            response = self._http.post(url, **kwargs)
        except httpx.HTTPError as error:
            raise ApiError(f"Cannot reach the API at {self._base_url}") from error
        if response.status_code >= 400:
            raise ApiError(_detail(response))
        return response.json()
