import uuid
from typing import Annotated

from fastapi import Depends

from app.domains.trades.exceptions import TradeDoesNotExistError
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

        await self.trade_repo.commit()

        return TradeResponse.model_validate(new_trade)

    async def get(self, trade_public_id: uuid.UUID, user_id: int) -> TradeResponse:
        trade = await self.trade_repo.get_trade_by_public_id_for_user(
            trade_public_id, user_id
        )

        if trade is None:
            raise TradeDoesNotExistError(
                f"There is no trade with public_id {trade_public_id} for user with id {user_id}"
            )

        return TradeResponse.model_validate(trade)


TradeServiceDependency = Annotated[TradeService, Depends(TradeService)]
