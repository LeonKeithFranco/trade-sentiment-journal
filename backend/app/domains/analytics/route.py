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
    """Return the current user's closed-trade profit and loss grouped by sentiment.

    Args:
        current_user: The authenticated user making the request.
        analytics_service: The injected AnalyticsService instance.

    Returns:
        list[SentimentVsReturnsResponse]: One entry per sentiment value, with count,
        average, and total profit and loss.
    """
    return await analytic_service.get_sentiment_vs_returns(current_user.id)


@router.get("/confidence-breakdown", response_model=list[ConfidenceBreakdownResponse])
async def get_confidence_breakdown(
    current_user: CurrentUserDependency, analytic_service: AnalyticServiceDependency
) -> list[ConfidenceBreakdownResponse]:
    """Return the current user's closed-trade profit and loss grouped by confidence bucket.

    Args:
        current_user: The authenticated user making the request.
        analytics_service: The injected AnalyticsService instance.

    Returns:
        list[ConfidenceBreakdownResponse]: One entry per confidence bucket (low, medium,
        high), with count, average, and total profict and loss.
    """
    return await analytic_service.get_confidence_breakdown(current_user.id)
