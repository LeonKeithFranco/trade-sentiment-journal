from decimal import Decimal

from pydantic import BaseModel

from app.domains.nlp.constants import SentimentEnum


class AnalyticBase(BaseModel):
    """Base schema for grouped trade performance analytics.

    Attributes:
        entry_count: The number of trades in this group.
        average_pnl: The average profit and loss across trades in this group.
        total_pnl: The total profit and loss across trades in this group.
    """

    entry_count: int
    average_pnl: Decimal
    total_pnl: Decimal


class SentimentVsReturnResponse(AnalyticBase):
    """Pydantic response model for the GET /analytics/sentiment-vs-returns endpoint.

    Attributes:
        sentiment: The journal sentiment value this group's stats correspond to.
    """

    sentiment: SentimentEnum


class ConfidenceBreakdownResponse(AnalyticBase):
    """Pydantic response model for the GET /analytics/confidence-breakdown endpoint.

    Attributes:
        confidence_band: The sentiment confidence bucket ("low", "medium", or "high") this
            group's stats correspond to.
    """

    confidence_band: str
