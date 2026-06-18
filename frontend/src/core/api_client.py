from typing import Any, Literal, Self

import httpx

from src.core.config import get_settings

_API_SETTINGS = get_settings().api


class APIClient:
    def __init__(self, token: str | None = None) -> None:
        headers: dict[str, str] = {"Accept": "application/json"}

        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        self._client: httpx.Client = httpx.Client(
            base_url=_API_SETTINGS.base_url,
            timeout=_API_SETTINGS.time_out,
            headers=headers,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self._client.close()

        return False

    def _request(
        self, method: Literal["GET", "POST", "PATCH", "DELETE"], endpoint: str, **kwargs
    ) -> httpx.Response:
        response = self._client.request(method, endpoint, **kwargs)
        response.raise_for_status()

        return response
