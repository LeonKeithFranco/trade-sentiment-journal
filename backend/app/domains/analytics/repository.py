from typing import Annotated

from fastapi import Depends
from sqlalchemy import (
    ColumnElement,
    RowMapping,
    case,
    func,
    select,
)
from sqlalchemy.orm import InstrumentedAttribute

from app.database import DbDependency
from app.database.repository import Repository
from app.models import JournalEntry, SentimentAnalysis, Trade


class AnalyticRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def _aggregate_helper(
        self, user_id: int, group_by_expr: ColumnElement | InstrumentedAttribute
    ) -> list[RowMapping]:
        query = (
            select(
                group_by_expr.label("group_key"),
                func.count().label("count"),
                func.avg(Trade.profit_and_loss).label("avg_pnl"),
                func.sum(Trade.profit_and_loss).label("total_pnl"),
            )
            .select_from(SentimentAnalysis)
            .join(SentimentAnalysis.journal_entry)
            .join(JournalEntry.trade)
            .where(Trade.user_id == user_id, Trade.closed_at.is_not(None))
            .group_by(group_by_expr)
            .order_by(group_by_expr)
        )
        results = await self.db.execute(query)

        return list(results.mappings().all())

    async def get_sentiment_vs_returns(self, user_id: int) -> list[RowMapping]:
        return await self._aggregate_helper(user_id, SentimentAnalysis._sentiment)

    async def get_confidence_breakdown(self, user_id: int) -> list[RowMapping]:
        confidence_bucket = case(
            (SentimentAnalysis.confidence < 0.5, "low"),
            (SentimentAnalysis.confidence < 0.75, "medium"),
            else_="high",
        )

        return await self._aggregate_helper(user_id, confidence_bucket)


AnalyticRepoDependency = Annotated[AnalyticRepository, Depends(AnalyticRepository)]
