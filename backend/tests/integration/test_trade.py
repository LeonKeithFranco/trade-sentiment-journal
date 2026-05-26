from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from app.models import Trade
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import Engine, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

_OPENED_AT = datetime.now(UTC).isoformat().removesuffix("+00:00") + "Z"
_CLOSED_AT = (
    datetime.now(UTC) + timedelta(days=1)  # noqa
).isoformat().removesuffix("+00:00") + "Z"


@pytest.fixture
def fake_jwt() -> str:
    return (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0."
        "KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
    )


class TestCreateTrade:
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
            "/trades",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_201_CREATED

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

    def test_add_trade_to_non_existent_user(
        self, client: TestClient, fake_jwt: str
    ) -> None:
        payload = {
            "ticker": "MAPPL",
            "direction": "LONG",
            "position_size": 3.33,
            "entry_price": 50.51,
            "exit_price": None,
            "opened_at": _OPENED_AT,
            "closed_at": None,
        }

        response = client.post(
            "/trades",
            headers={"Authorization": f"Bearer {fake_jwt}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        detail = response.json()["detail"]

        assert detail == "Token is invalid"

    @pytest.mark.parametrize(
        "payload",
        [
            {
                "ticker": "MAPPL",
                "direction": "LONG",
                "position_size": 3.33,
                "entry_price": 50.51,
                "exit_price": 6.7,
                "opened_at": _OPENED_AT,
                "closed_at": None,
            },
            {
                "ticker": "GNG",
                "direction": "SHORT",
                "position_size": 1.01,
                "entry_price": 34.56,
                "exit_price": None,
                "opened_at": _OPENED_AT,
                "closed_at": _CLOSED_AT,
            },
        ],
    )
    def test_closed_at_or_exit_price_one_none(
        self, client: TestClient, access_token: str, payload: dict
    ) -> None:
        response = client.post(
            "/trades",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        detail = response.json()["detail"][0]

        assert detail == {
            "type": "value_error",
            "loc": ["body"],
            "msg": "Value error, exit_price and closed_at must both be None or must both "
            "have values",
            "input": payload,
            "ctx": {"error": {}},
        }

    def test_closed_at_before_opened_at(
        self, client: TestClient, access_token: str
    ) -> None:
        payload = {
            "ticker": "BSLA",
            "direction": "LONG",
            "position_size": 1,
            "entry_price": 1,
            "exit_price": 2,
            "opened_at": _CLOSED_AT,
            "closed_at": _OPENED_AT,
        }

        response = client.post(
            "/trades",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        detail = response.json()["detail"][0]

        assert detail == {
            "type": "value_error",
            "loc": ["body"],
            "msg": "Value error, closed_at should be later than opened_at",
            "input": payload,
            "ctx": {"error": {}},
        }

    def test_direction_constraint(
        self,
        db_engine: Engine,
        access_token: str,  # here to make sure a use is in the db
    ) -> None:
        with pytest.raises(IntegrityError):
            with Session(db_engine) as session:
                query = insert(Trade).values(
                    {
                        "user_id": 1,
                        "ticker": "MAPPL",
                        "_direction": "FAKE",
                        "position_size": 3.33,
                        "entry_price": 50.51,
                        "exit_price": None,
                        "opened_at": _OPENED_AT,
                        "closed_at": None,
                    }
                )

                session.execute(query)

    def test_closed_at_after_opened_at_constraint(
        self,
        db_engine: Engine,
        access_token: str,  # here to make sure a use is in the db
    ) -> None:
        with pytest.raises(IntegrityError):
            with Session(db_engine) as session:
                query = insert(Trade).values(
                    {
                        "user_id": 1,
                        "ticker": "MAPPL",
                        "_direction": "LONG",
                        "position_size": 3.33,
                        "entry_price": 50.51,
                        "exit_price": 100.11,
                        "opened_at": _CLOSED_AT,
                        "closed_at": _OPENED_AT,
                    }
                )

                session.execute(query)

    @pytest.mark.parametrize(
        "values,pnl",
        [
            (
                {
                    "ticker": "BSLA",
                    "_direction": "LONG",
                    "position_size": 1,
                    "entry_price": 1,
                    "exit_price": 2,
                    "opened_at": _OPENED_AT,
                    "closed_at": _CLOSED_AT,
                    "user_id": 1,
                },
                1,
            ),
            (
                {
                    "ticker": "DRK",
                    "_direction": "SHORT",
                    "position_size": 1,
                    "entry_price": 1,
                    "exit_price": 2,
                    "opened_at": _OPENED_AT,
                    "closed_at": _CLOSED_AT,
                    "user_id": 1,
                },
                -1,
            ),
        ],
    )
    def test_calculate_pnl_event(
        self,
        db_engine: Engine,
        access_token: str,  # here to make sure a use is in the db
        values: dict,
        pnl: Decimal,
    ) -> None:
        with Session(db_engine) as session:
            trade = Trade(**values)

            session.add(trade)
            session.commit()

            session.refresh(trade)

            assert trade is not None
            assert trade.profit_and_loss is not None
            assert str(trade.profit_and_loss) == f"{pnl:.2f}"
