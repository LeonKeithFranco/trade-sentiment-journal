from datetime import UTC, datetime
from decimal import Decimal

import pytest
from app.domains.nlp.constants import SentimentEnum
from app.domains.trades.constants import Direction
from app.models import JournalEntry, SentimentAnalysis, Trade, User
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def seed_db(
    client: TestClient, access_token: str, email: str, db_engine: Engine
) -> None:
    with Session(db_engine) as session:
        user = session.execute(select(User).where(User.email == email)).scalar_one()

        trade_win = Trade()
        trade_win.ticker = "WIN"
        trade_win.direction = Direction.LONG
        trade_win.position_size = Decimal("2.00")
        trade_win.entry_price = Decimal("100.00")
        trade_win.exit_price = Decimal("150.00")
        trade_win.opened_at = datetime(2026, 1, 1, tzinfo=UTC)
        trade_win.closed_at = datetime(2026, 1, 2, tzinfo=UTC)
        trade_win.user_id = user.id

        trade_loss = Trade()
        trade_loss.ticker = "LOSS"
        trade_loss.direction = Direction.SHORT
        trade_loss.position_size = Decimal("1.00")
        trade_loss.entry_price = Decimal("100.00")
        trade_loss.exit_price = Decimal("150.00")
        trade_loss.opened_at = datetime(2026, 1, 3, tzinfo=UTC)
        trade_loss.closed_at = datetime(2026, 1, 4, tzinfo=UTC)
        trade_loss.user_id = user.id

        session.add_all((trade_win, trade_loss))
        session.flush()

        entry_pos = JournalEntry()
        entry_pos.title = "Win Entry"
        entry_pos.entry = "I am very bullish about this obviously winning trade."
        entry_pos.user_id = user.id
        entry_pos.trade_id = trade_win.id

        entry_neg = JournalEntry()
        entry_neg.title = "Loss Entry"
        entry_neg.entry = (
            "I am very bearish about this trdae because it feels like a loss."
        )
        entry_neg.user_id = user.id
        entry_neg.trade_id = trade_loss.id

        session.add_all((entry_pos, entry_neg))
        session.flush()

        sa_pos = SentimentAnalysis()
        sa_pos.sentiment = SentimentEnum.POSITIVE
        sa_pos.confidence = 0.85
        sa_pos.journal_entry_id = entry_pos.id

        sa_neg = SentimentAnalysis()
        sa_neg.sentiment = SentimentEnum.NEGATIVE
        sa_neg.confidence = 0.6
        sa_neg.journal_entry_id = entry_neg.id

        session.add_all((sa_pos, sa_neg))

        session.commit()


class TestConfidenceBreakdown:
    def test_confidence_breakdown(self, client: TestClient, access_token: str) -> None:
        response = client.get(
            "/analytics/confidence-breakdown",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 2

        confidence_bands = {item["confidence_band"]: item for item in data}

        assert "high" in confidence_bands
        assert confidence_bands["high"]["entry_count"] == 1
        assert Decimal(confidence_bands["high"]["average_pnl"]) == Decimal("100.00")
        assert Decimal(confidence_bands["high"]["total_pnl"]) == Decimal("100.00")

        assert "medium" in confidence_bands
        assert confidence_bands["medium"]["entry_count"] == 1
        assert Decimal(confidence_bands["medium"]["average_pnl"]) == Decimal("-50.00")
        assert Decimal(confidence_bands["medium"]["total_pnl"]) == Decimal("-50.00")

    def test_no_data(self, client: TestClient, other_access_token: str) -> None:
        response = client.get(
            "/analytics/confidence-breakdown",
            headers={"Authorization": f"Bearer {other_access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_unauthorized(self, client: TestClient, fake_access_token: str) -> None:
        response = client.get(
            "/analytics/confidence-breakdown",
            headers={"Authorization": f"Bearer {fake_access_token}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSentimentVsReturns:
    def test_sentiment_vs_returns(self, client: TestClient, access_token: str) -> None:
        response = client.get(
            "/analytics/sentiment-vs-returns",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data) == 2

        sentiments = {item["sentiment"]: item for item in data}

        assert "positive" in sentiments
        assert sentiments["positive"]["entry_count"] == 1
        assert Decimal(sentiments["positive"]["average_pnl"]) == Decimal("100.00")
        assert Decimal(sentiments["positive"]["total_pnl"]) == Decimal("100.00")

        assert "negative" in sentiments
        assert sentiments["negative"]["entry_count"] == 1
        assert Decimal(sentiments["negative"]["average_pnl"]) == Decimal("-50.00")
        assert Decimal(sentiments["negative"]["total_pnl"]) == Decimal("-50.00")

    def test_no_data(self, client: TestClient, other_access_token: str) -> None:
        response = client.get(
            "/analytics/sentiment-vs-returns",
            headers={"Authorization": f"Bearer {other_access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_unauthorized(self, client: TestClient, fake_access_token: str) -> None:
        response = client.get(
            "/analytics/sentiment-vs-returns",
            headers={"Authorization": f"Bearer {fake_access_token}"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
