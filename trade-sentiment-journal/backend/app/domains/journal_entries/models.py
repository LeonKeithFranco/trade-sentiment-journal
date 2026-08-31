from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MAX_TITLE_LENGTH
from app.database import Base
from app.database.columns import TradeIDColumn, UserIDColumn
from app.database.mixins import PublicIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models import SentimentAnalysis, Trade, User


class JournalEntry(PublicIdMixin, TimestampMixin, Base):
    """ORM model representing a trader's journal entry for a trade.

    Attributes:
        id: Auto-incremented primary key inherited from Base.
        public_id: A randomly generated, unique UUID for external references.
        created_on: The UTC timestamp when the row was inserted.
        updated_on: The UTC timestamp when the row was last updated.
        title: An optional short title for the journal entry.
        entry: The full text content of the journal entry.
        user_id: The ID of the User who wrote this entry.
        trade_id: The ID of the Trade this entry is about.
        user: The associated User record.
        trade: The associated Trade record.
        sentiment_analysis: The SentimentAnalysis record derived from this
            entry's text, if one has been generated.
    """

    __tablename__ = "journal_entries"

    title: Mapped[str | None] = mapped_column(
        String(MAX_TITLE_LENGTH),
    )
    entry: Mapped[str] = mapped_column(
        Text(),
    )

    user_id: Mapped[UserIDColumn]
    trade_id: Mapped[TradeIDColumn]

    user: Mapped["User"] = relationship(
        back_populates="journal_entries",
    )

    trade: Mapped["Trade"] = relationship(
        back_populates="journal_entries",
    )

    sentiment_analysis: Mapped["SentimentAnalysis"] = relationship(
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )
