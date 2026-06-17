from decimal import Decimal
from typing import Annotated

from fastapi import Depends

from app.domains.analytics.repository import AnalyticRepoDependency, AnalyticRepository
from app.domains.analytics.schemas import (
    ConfidenceBreakdownResponse,
    SentimentVsReturnResponse,
)


class AnalyticService:
    def __init__(
        self,
        analytic_repo: AnalyticRepoDependency,
    ) -> None:
        self.analytic_repo: AnalyticRepository = analytic_repo

    async def get_sentiment_vs_returns(
        self, user_id: int
    ) -> list[SentimentVsReturnResponse]:
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
