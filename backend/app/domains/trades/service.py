from typing import Annotated

from fastapi import Depends

from app.domains.trades.repository import TradeRepoDependency, TradeRepository
from app.domains.trades.schemas import TradeRequest, TradeResponse


class TradeService:
    def __init__(
        self,
        trade_repo: TradeRepoDependency,
    ) -> None:
        self.trade_repo: TradeRepository = trade_repo

    async def create(self, trade_info: TradeRequest, user_id: int) -> TradeResponse:
        new_trade = await self.trade_repo.insert_trade(trade_info, user_id)

        return TradeResponse.model_validate(new_trade)


TradeServiceDependency = Annotated[TradeService, Depends(TradeService)]
