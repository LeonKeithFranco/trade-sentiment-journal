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
    """ORM model representing the sentiment analysis of a journal entry.

    Attributes:
        id: Auto-incremented primary key inherited from Base.
        public_id: A randomly generated, unique UUID for external references.
        created_on: The UTC timestamp when the row was inserted.
        updated_on: The UTC timestamp when the row was last updated.
        sentiment: The predicted sentiment classification.
        confidence: The model's confidence in the predicted sentiment,
            strictly between 0.0 and 1.0.
        journal_entry_id: The ID of the JournalEntry this analysis was
            generated from.
        journal_entry: The associated JournalEntry record.
    """

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
        """Get the sentiment classification as a SentimentEnum.

        Returns:
            SentimentEnum: The parsed sentiment value.
        """
        return SentimentEnum(self._sentiment)

    @sentiment.setter
    def sentiment(self, sentiment: SentimentEnum) -> None:
        """Set the sentiment classification from a SentimentEnum.

        Args:
            sentiment: The sentiment value to store.
        """
        self._sentiment = sentiment.value

    confidence: Mapped[float] = mapped_column(
        Numeric(5, 4),
    )

    journal_entry_id: Mapped[JournalEntryIDColumn]

    journal_entry: Mapped["JournalEntry"] = relationship(
        back_populates="sentiment_analysis",
    )
