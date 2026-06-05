from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.database.columns import JournalEntryIDColumn
from app.database.mixins import PublicIdMixin, TimestampMixin
from app.domains.nlp.constants import SentimentEnum

if TYPE_CHECKING:
    from app.models import JournalEntry


class SentimentAnalysis(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "sentiment_analysis"

    __table_args__ = (
        CheckConstraint(
            "sentiment in ('negative','neutral','positive')", name="check_sentiment"
        ),
        CheckConstraint(
            "confidence > 0.0 AND confidence < 1.0", name="check_confidence_range"
        ),
    )

    _sentiment: Mapped[str] = mapped_column(
        String(10),
        name="sentiment",
    )

    @property
    def sentiment(self) -> SentimentEnum:
        return SentimentEnum(self._sentiment)

    @sentiment.setter
    def sentiment(self, sentiment: SentimentEnum) -> None:
        self._sentiment = sentiment.value

    confidence: Mapped[float] = mapped_column(
        Numeric(5, 4),
    )

    journal_entry_id: Mapped[JournalEntryIDColumn]

    journal_entry: Mapped["JournalEntry"] = relationship(
        back_populates="sentiment_analysis",
    )
