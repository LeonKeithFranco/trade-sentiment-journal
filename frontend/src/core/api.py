from datetime import datetime
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

        return response

    def _login_register_helper(
        self, email: str, password: str, endpoint: Literal["register", "login"]
    ) -> httpx.Response:
        return self._request(
            "POST", f"/auth/{endpoint}", json={"email": email, "password": password}
        )

    def post_register(self, email: str, password: str) -> httpx.Response:
        return self._login_register_helper(email, password, endpoint="register")

    def post_login(self, email: str, password: str) -> httpx.Response:
        return self._login_register_helper(email, password, endpoint="login")

    def post_trade(
        self,
        ticker: str,
        direction: str,
        position_size: float,
        entry_price: float,
        opened_at: datetime,
        exit_price: float | None,
        closed_at: datetime | None,
    ) -> httpx.Response:
        return self._request(
            "POST",
            "/trades",
            json={
                "ticker": ticker,
                "direction": direction,
                "position_size": position_size,
                "entry_price": entry_price,
                "opened_at": opened_at.isoformat(),
                "exit_price": exit_price,
                "closed_at": closed_at.isoformat() if closed_at else None,
            },
        )

    def get_all_trades(self) -> httpx.Response:
        return self._request("GET", "/trades")


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
