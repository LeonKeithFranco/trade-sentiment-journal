import uuid
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import CursorResult, delete

from app.database import DbDependency
from app.database.repository import Repository
from app.models import Trade

type MaybeTrade = Trade | None


class TradeRepository(Repository[Trade]):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def insert_trade(self, **create_info) -> Trade:
        return await self.insert_into_table(Trade, **create_info)

    async def get_trade_by_public_id_for_user(
        self, trade_public_id: uuid.UUID, user_id: int
    ) -> MaybeTrade:
        return await self.get_from_table_by(
            Trade, Trade.public_id == trade_public_id, Trade.user_id == user_id
        )

    async def get_all_trades_by_user_id(self, user_id: int) -> list[Trade]:
        return await self.get_all_from_table(Trade, Trade.user_id == user_id)

    async def delete_trade_by_public_id_for_user(
        self, trade_public_id: uuid.UUID, user_id: int
    ) -> int:
        return await self.delete_from_table_by(
            Trade, Trade.public_id == trade_public_id, Trade.user_id == user_id
        )

    async def update_trade(
        self,
        trade: Trade,
        /,
        **update_info,
    ) -> Trade:
        for key, val in update_info.items():
            setattr(trade, key, val)

        await self.db.flush()
        await self.db.refresh(trade)

        return trade


TradeRepoDependency = Annotated[TradeRepository, Depends(TradeRepository)]
