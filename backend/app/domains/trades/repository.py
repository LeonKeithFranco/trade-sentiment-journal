import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.database import DbDependency
from app.database.repository import Repository
from app.domains.trades.constants import Direction
from app.models import Trade

type MaybeTrade = Trade | None


class TradeRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def insert_trade(
        self,
        ticker: str,
        direction: Direction,
        position_size: Decimal,
        entry_price: Decimal,
        opened_at: datetime,
        user_id: int,
        exit_price: Decimal | None = None,
        closed_at: datetime | None = None,
    ) -> Trade:
        trade = Trade()
        trade.ticker = ticker
        trade.direction = direction
        trade.position_size = position_size
        trade.entry_price = entry_price
        trade.exit_price = exit_price
        trade.opened_at = opened_at
        trade.closed_at = closed_at
        trade.user_id = user_id

        self.db.add(trade)
        await self.db.flush()
        await self.db.refresh(trade)

        return trade

    async def get_trade_by_public_id_for_user(
        self, trade_public_id: uuid.UUID, user_id: int
    ) -> MaybeTrade:
        query = (
            select(Trade)
            .where(Trade.public_id == trade_public_id)
            .where(Trade.user_id == user_id)
        )
        results = await self.db.execute(query)
        trade = results.scalar_one_or_none()

        return trade

    async def get_all_trades_by_user_id(self, user_id: int) -> list[Trade]:
        query = select(Trade).where(Trade.user_id == user_id)
        results = await self.db.execute(query)
        trades = results.scalars().all()

        return list(trades)


TradeRepoDependency = Annotated[TradeRepository, Depends(TradeRepository)]
