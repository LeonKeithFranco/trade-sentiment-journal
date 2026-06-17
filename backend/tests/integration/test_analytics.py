from datetime import UTC, datetime
from decimal import Decimal

import pytest
from app.domains.nlp.constants import SentimentEnum
from app.domains.trades.constants import Direction
from app.models import JournalEntry, SentimentAnalysis, Trade, User
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

        sa_pos = SentimentAnalysis()
        sa_pos.sentiment = SentimentEnum.NEGATIVE
        sa_pos.confidence = 0.6
        sa_pos.journal_entry_id = entry_neg.id

        session.add_all((sa_pos, sa_pos))

        session.commit()


class TestAnalytics:
    pass
