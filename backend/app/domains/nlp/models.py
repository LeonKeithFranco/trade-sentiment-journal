from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import PublicIdMixin, TimestampMixin
from app.domains.nlp.constants import SentimentEnum


class SentimentAnalysis(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "sentiment_analysis"

    __table_args__ = (
        CheckConstraint(
            "sentiment in ('negative','neutral','positive')", name="check_sentiment"
        ),
    )

    _sentiment: Mapped[str] = mapped_column(
        String(10),
        name="sentiment",
    )

    @property
    def direction(self) -> SentimentEnum:
        return SentimentEnum(self._sentiment)

    @direction.setter
    def direction(self, sentiment: SentimentEnum) -> None:
        self._sentiment = sentiment.value
