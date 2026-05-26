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
        trade_info_dict = trade_info.model_dump(exclude_unset=True)

        new_trade = await self.trade_repo.insert_trade(
            user_id=user_id, **trade_info_dict
        )

        return TradeResponse.model_validate(new_trade)


TradeServiceDependency = Annotated[TradeService, Depends(TradeService)]
