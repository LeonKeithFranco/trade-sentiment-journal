from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlalchemy import RowMapping

from app.domains.analytics.repository import AnalyticRepoDependency, AnalyticRepository
from app.domains.analytics.schemas import SentimentVsReturnResponse


class AnalyticService:
    def __init__(
        self,
        analytic_repo: AnalyticRepoDependency,
    ) -> None:
        self.analytic_repo: AnalyticRepository = analytic_repo

    async def _get_helper(
        self, user_id: int, results: list[RowMapping]
    ) -> list[SentimentVsReturnResponse]:
        return [
            SentimentVsReturnResponse(
                entry_count=result["count"],
                average_pnl=Decimal(result["avg_pnl"]),
                total_pnl=Decimal(result["total_pnl"]),
                sentiment=result["group_key"],
            )
            for result in results
        ]

    async def get_sentiment_vs_returns(
        self, user_id: int
    ) -> list[SentimentVsReturnResponse]:
        return await self._get_helper(
            user_id, results=await self.analytic_repo.get_sentiment_vs_returns(user_id)
        )

    async def get_confidence_breakdown(
        self, user_id: int
    ) -> list[SentimentVsReturnResponse]:
        return await self._get_helper(
            user_id, results=await self.analytic_repo.get_confidence_breakdown(user_id)
        )


AnalyticServiceDependency = Annotated[AnalyticService, Depends(AnalyticService)]
