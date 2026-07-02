from http import HTTPStatus
from typing import Any, Literal, Self, cast

import httpx
import streamlit as st

from src.core.config import get_settings

_API_SETTINGS = get_settings().api


class _APIClient:
    """HTTP client for communicating with the FastAPI backend.

    Wraps an httpx.Client configured with the backend's base URL, timeout,
    and an optional bearer token. Intended to be used as a context manager
    so the underlying connection is properly closed after use.
    """

    def __init__(self, token: str | None = None) -> None:
        """Initialize the client with an optional bearer token.

        Args:
            token: The access token to send as a Bearer Authorization
                header, or None to make an unauthenticated request.
        """
        headers: dict[str, str] = {"Accept": "application/json"}

        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        self._client: httpx.Client = httpx.Client(
            base_url=_API_SETTINGS.base_url,
            timeout=_API_SETTINGS.time_out,
            headers=headers,
        )

    def __enter__(self) -> Self:
        """Enter the context manager.

        Returns:
            _APIClient: The _APIClient instance itself.
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit the context manager and close the HTTP connection.

        Args:
            exc_type: The exception type if an exception occurred, None otherwise.
            exc_val: The exception value if an exception occurred, None otherwise.
            exc_tb: The exception traceback if an exception occurred, None otherwise.

        Returns:
            bool: False to propagate exceptions.
        """
        self._client.close()

        return False

    def request(
        self, method: Literal["GET", "POST", "PATCH", "DELETE"], endpoint: str, **kwargs
    ) -> httpx.Response:
        """Send an HTTP request to the backend.

        Args:
            method: The HTTP method to use.
            endpoint: The API endpoint path to request.
            **kwargs: Additional keyword arguments passed through to
                httpx.Client.request (e.g. json, params).

        Returns:
            httpx.Response: The raw HTTP response from the backend.
        """
        response = self._client.request(method, endpoint, **kwargs)

        return response


def make_api_request(
    method: Literal["GET", "POST", "PATCH", "DELETE"], endpoint: str, **kwargs
) -> httpx.Response:
    """Send an authenticated request to the backend, refreshing the access token if needed.

    Uses the access token from session state. If the request fails with 401
    Unauthorized and a refresh token is available, attempts to refresh the
    access token and retries the request once with the new token.

    Args:
        method: The HTTP method to use.
        endpoint: The API endpoint path to request.
        **kwargs: Additional keyword arguments passed through to the
            underlying HTTP request (e.g. json, params).

    Returns:
        httpx.Response: The response from the backend, either from the
            original request or the retried request after a token refresh.
    """
    with _APIClient(token=st.session_state["access_token"]) as client:
        response = client.request(method, endpoint, **kwargs)

        if (
            response.status_code == HTTPStatus.UNAUTHORIZED
            and st.session_state["refresh_token"]
        ):
            refresh_response = client.request(
                "POST",
                "/auth/refresh",
                json={"refresh_token": st.session_state["refresh_token"]},
            )

            if refresh_response.status_code == HTTPStatus.OK:
                st.session_state["access_token"] = refresh_response.json()[
                    "access_token"
                ]
                st.session_state["refresh_token"] = refresh_response.json()[
                    "refresh_token"
                ]

                with _APIClient(token=st.session_state["access_token"]) as client:
                    response = client.request(method, endpoint, **kwargs)

        return response


def get_all_trades() -> list[dict[str, Any]]:
    """Fetch all trades belonging to the current user from the backend.

    Returns:
        list[dict[str, Any]]: The JSON-decoded trade objects returned by the
            backend.
    """
    response = make_api_request("GET", "/trades")
    trades = cast(list[dict[str, Any]], response.json())

    return trades


def convert_pydantic_error_to_human_readable_message(
    err_detail: dict, general_err_msg: str
) -> str:
    """Convert a raw Pydantic validation error into a user-friendly message.

    Handles a few common validation error types (too-short strings, custom
    value errors, and greater-than constraints) with tailored phrasing;
    falls back to a general error message for any other error type.

    Args:
        err_detail: A single error entry from a FastAPI validation error
            response's "detail" list.
        general_err_msg: The fallback message to use for error types without
            specific handling.

    Returns:
        str: A human-readable error message, ending in a period.
    """
    msg = ""

    match err_detail["type"]:
        case "string_too_short":
            field = str(err_detail["loc"][-1])

            msg = str(err_detail["msg"]).replace("String", field.capitalize())
        case "value_error":
            msg = (
                str(err_detail["msg"])
                .replace("Value error,", "")
                .replace("value is not a valid email address: ", "")
            )
        case "greater_than":
            field = str(err_detail["loc"][-1])

            msg = str(err_detail["msg"]).replace(
                "Input", field.replace("_", " ").title()
            )
        case _:
            msg = general_err_msg

    return msg + ("." if msg[-1] != "." else "")
