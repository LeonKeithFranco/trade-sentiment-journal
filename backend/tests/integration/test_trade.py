from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi import status
from fastapi.testclient import TestClient

_OPENED_AT = datetime.now(UTC).isoformat().removesuffix("+00:00") + "Z"
_CLOSED_AT = (
    datetime.now(UTC) + timedelta(days=1)  # noqa: F401
).isoformat().removesuffix("+00:00") + "Z"


class TestCreate:
    @pytest.mark.parametrize(
        "payload,pnl",
        [
            (
                {
                    "ticker": "MAPPL",
                    "direction": "LONG",
                    "position_size": 3.33,
                    "entry_price": 50.51,
                    "exit_price": None,
                    "opened_at": _OPENED_AT,
                    "closed_at": None,
                },
                None,
            ),
            (
                {
                    "ticker": "GNG",
                    "direction": "SHORT",
                    "position_size": 1.01,
                    "entry_price": 34.56,
                    "exit_price": None,
                    "opened_at": _OPENED_AT,
                    "closed_at": None,
                },
                None,
            ),
            (
                {
                    "ticker": "BSLA",
                    "direction": "LONG",
                    "position_size": 1,
                    "entry_price": 1,
                    "exit_price": 2,
                    "opened_at": _OPENED_AT,
                    "closed_at": _CLOSED_AT,
                },
                1,
            ),
            (
                {
                    "ticker": "DRK",
                    "direction": "SHORT",
                    "position_size": 1,
                    "entry_price": 1,
                    "exit_price": 2,
                    "opened_at": _OPENED_AT,
                    "closed_at": _CLOSED_AT,
                },
                -1,
            ),
        ],
    )
    def test_create_trade(
        self, client: TestClient, access_token: str, payload: dict, pnl: Decimal | None
    ) -> None:
        response = client.post(
            "/trade",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["ticker"] == payload["ticker"]
        assert data["direction"] == payload["direction"]
        assert data["position_size"] == f"{payload['position_size']:.2f}"
        assert data["entry_price"] == f"{payload['entry_price']:.2f}"
        assert data["exit_price"] == (
            f"{payload['exit_price']:.2f}"
            if payload["exit_price"] is not None
            else None
        )
        assert data["opened_at"] == payload["opened_at"]
        assert data["closed_at"] == (
            payload["closed_at"] if payload["closed_at"] is not None else None
        )
        assert data["profit_and_loss"] == (f"{pnl:.2f}" if pnl is not None else None)
        assert "public_id" in data
        assert "created_on" in data
        assert "updated_on" in data
