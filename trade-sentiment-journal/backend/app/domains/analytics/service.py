from decimal import Decimal
from typing import Annotated

from fastapi import Depends

from app.domains.analytics.repository import AnalyticRepoDependency, AnalyticRepository
from app.domains.analytics.schemas import (
    ConfidenceBreakdownResponse,
    SentimentVsReturnResponse,
)


class AnalyticService:
    """Service layer for computing sentiment-vs-performance analytics.

    Attributes:
        analytic_repo: The repository used for database access.
    """

    def __init__(
        self,
        analytic_repo: AnalyticRepoDependency,
    ) -> None:
        """Initialize the service with an injected analytic repository.

        Args:
            analytic_repo: The AnalyticRepository instance, provided by
                FastAPI's dependency injection.
        """
        self.analytic_repo: AnalyticRepository = analytic_repo

    async def get_sentiment_vs_returns(
        self, user_id: int
    ) -> list[SentimentVsReturnResponse]:
        """Compute a user's closed-trade profit and loss grouped by sentiment.

        Args:
            user_id: The ID of the user whose trades to aggregate.

        Returns:
            list[SentimentVsReturnResponse]: One entry per sentiment value,
                with count, average, and total profit and loss.
        """
        results = await self.analytic_repo.get_sentiment_vs_returns(user_id)

        return [
            SentimentVsReturnResponse(
                entry_count=result["count"],
                average_pnl=Decimal(result["avg_pnl"]),
                total_pnl=Decimal(result["total_pnl"]),
                sentiment=result["group_key"],
            )
            for result in results
        ]

    async def get_confidence_breakdown(
        self, user_id: int
    ) -> list[ConfidenceBreakdownResponse]:
        """Compute a user's closed-trade profit and loss grouped by confidence bucket.

        Args:
            user_id: The ID of the user whose trades to aggregate.

        Returns:
            list[ConfidenceBreakdownResponse]: One entry per confidence
                bucket (low, medium, high), with count, average, and total
                profit and loss.
        """
        results = await self.analytic_repo.get_confidence_breakdown(user_id)

        return [
            ConfidenceBreakdownResponse(
                entry_count=result["count"],
                average_pnl=Decimal(result["avg_pnl"]),
                total_pnl=Decimal(result["total_pnl"]),
                confidence_band=result["group_key"],
            )
            for result in results
        ]


AnalyticServiceDependency = Annotated[AnalyticService, Depends(AnalyticService)]
