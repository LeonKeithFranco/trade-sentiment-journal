from decimal import Decimal

from pydantic import BaseModel

from app.domains.nlp.constants import SentimentEnum


class AnalyticBase(BaseModel):
    entry_count: int
    average_pnl: Decimal
    total_pnl: Decimal


class SentimentVsReturnResponse(AnalyticBase):
    sentiment: SentimentEnum


class ConfidenceBreakdownResponse(AnalyticBase):
    confidence_band: str
