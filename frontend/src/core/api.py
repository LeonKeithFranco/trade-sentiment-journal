from http import HTTPStatus
from typing import Any, Literal, Self, cast

import httpx
import streamlit as st

from src.core.config import get_settings

_API_SETTINGS = get_settings().api


class _APIClient:
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

    def request(
        self, method: Literal["GET", "POST", "PATCH", "DELETE"], endpoint: str, **kwargs
    ) -> httpx.Response:
        response = self._client.request(method, endpoint, **kwargs)

        return response


def make_api_request(
    method: Literal["GET", "POST", "PATCH", "DELETE"], endpoint: str, **kwargs
) -> httpx.Response:
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
    response = make_api_request("GET", "/trades")
    trades = cast(list[dict[str, Any]], response.json())

    return trades


def convert_pydantic_error_to_human_readable_message(
    err_detail: dict, general_err_msg: str
) -> str:
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
