from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository
from app.domains.trades.constants import Direction
from app.models import Trade


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
        profit_and_loss: Decimal | None = None,
        closed_at: datetime | None = None,
    ) -> Trade:
        trade = Trade()
        trade.ticker = ticker
        trade.direction = direction
        trade.position_size = position_size
        trade.entry_price = entry_price
        trade.exit_price = exit_price
        trade.profit_and_loss = profit_and_loss
        trade.opened_at = opened_at
        trade.closed_at = closed_at
        trade.user_id = user_id

        self.db.add(trade)
        await self.db.flush()
        await self.db.refresh(trade)

        return trade


TradeRepoDependency = Annotated[TradeRepository, Depends(TradeRepository)]
