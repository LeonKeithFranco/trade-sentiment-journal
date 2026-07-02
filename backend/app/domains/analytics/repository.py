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
    """Data-access layer for aggregate sentiment-vs-performance analytics.

    Wraps an async SQLAlchemy session and provides queries that join SentimentAnalysis,
    JournalEntry, and Trade to produce grouped profit and loss statistics for a user's
    closed trades.

    Attributes:
        db: The underlying async SQLAlchemy session.
    """

    def __init__(self, db: DbDependency) -> None:
        """Initialize the repository with a database session.

        Args:
            db: An async SQLAlchemy session, provided by the FastAPI's dependency
            injection via get_db.
        """
        super().__init__(db)

    async def _aggregate_helper(
        self, user_id: int, group_by_expr: ColumnElement | InstrumentedAttribute
    ) -> list[RowMapping]:
        """Aggregate a user's closed-trade profit and loss by an arbitrary grouping.

        Joins sentiment analyses to their journal entries and trades, restricts to the
        given user's closed trades, and groups by the provided expression, computing the
        count of trades, average profit and loss, and total profit loss per group.

        Args:
            user_id: The ID of the user whose trades to aggregate.
            group_by_expr: The column or expression to group results by.

        Returns:
            list[RowMapping]: One row per distinct group, each containing group_key,
                count, avg_pnl, and total_pnl.
        """
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
        """Aggregate a user's closed-trade profit and loss by sentiment confidence bucket.

        Buckets sentiment analyses into "low" (< 0.5), "medium" (< 0.75), and "high"
        confidence groups before aggregating.

        Args:
            user_id: The ID of the user whose trades to aggregate.

        Returns:
            list[RowMapping]: One row per confdience bucket, each containing count,
            avg_pnl, and total_pnl.
        """
        return await self._aggregate_helper(user_id, SentimentAnalysis._sentiment)

    async def get_confidence_breakdown(self, user_id: int) -> list[RowMapping]:
        confidence_bucket = case(
            (SentimentAnalysis.confidence < 0.5, "low"),
            (SentimentAnalysis.confidence < 0.75, "medium"),
            else_="high",
        )

        return await self._aggregate_helper(user_id, confidence_bucket)


AnalyticRepoDependency = Annotated[AnalyticRepository, Depends(AnalyticRepository)]
