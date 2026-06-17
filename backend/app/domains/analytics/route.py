from fastapi import APIRouter

from app.domains.analytics.schemas import (
    ConfidenceBreakdownResponse,
    SentimentVsReturnResponse,
)
from app.domains.analytics.service import AnalyticServiceDependency
from app.security import CurrentUserDependency

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sentiment-vs-returns", response_model=list[SentimentVsReturnResponse])
async def get_sentiment_vs_returns(
    current_user: CurrentUserDependency, analytic_service: AnalyticServiceDependency
) -> list[SentimentVsReturnResponse]:
    return await analytic_service.get_sentiment_vs_returns(current_user.id)


@router.get("/confidence-breakdown", response_model=list[ConfidenceBreakdownResponse])
async def get_confidence_breakdown(
    current_user: CurrentUserDependency, analytic_service: AnalyticServiceDependency
) -> list[ConfidenceBreakdownResponse]:
    return await analytic_service.get_confidence_breakdown(current_user.id)
