from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository
from app.domains.trade.schemas import TradeRequest
from app.models import Trade


class TradeRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def insert_trade(self, trade_info: TradeRequest, user_id: int) -> Trade:
        trade = Trade(**trade_info.model_dump(exclude_unset=True))
        trade.user_id = user_id

        self.db.add(trade)
        await self.db.flush()
        await self.db.refresh(trade)

        return trade


TradeRepoDependency = Annotated[TradeRepository, Depends(TradeRepository)]
