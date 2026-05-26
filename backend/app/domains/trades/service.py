import uuid
from typing import Annotated

from fastapi import Depends

from app.domains.trades.exceptions import TradeDoesNotExistError
from app.domains.trades.repository import TradeRepoDependency, TradeRepository
from app.domains.trades.schemas import (
    TradeCreateRequest,
    TradeResponse,
    TradeUpdateRequest,
)
from app.models import Trade


class TradeService:
    def __init__(
        self,
        trade_repo: TradeRepoDependency,
    ) -> None:
        self.trade_repo: TradeRepository = trade_repo

    async def _get_helper(self, trade_public_id: uuid.UUID, user_id: int) -> Trade:
        trade = await self.trade_repo.get_trade_by_public_id_for_user(
            trade_public_id, user_id
        )

        if trade is None:
            raise TradeDoesNotExistError(
                f"There is no trade with public_id {trade_public_id} for user with id {user_id}"
            )

        return trade

    async def create(
        self, trade_info: TradeCreateRequest, user_id: int
    ) -> TradeResponse:
        trade_info_dict = trade_info.model_dump(exclude_unset=True)

        new_trade = await self.trade_repo.insert_trade(
            user_id=user_id, **trade_info_dict
        )

        await self.trade_repo.commit()

        return TradeResponse.model_validate(new_trade)

    async def get(self, trade_public_id: uuid.UUID, user_id: int) -> TradeResponse:
        trade = await self._get_helper(trade_public_id, user_id)

        return TradeResponse.model_validate(trade)

    async def get_all(self, user_id: int) -> list[TradeResponse]:
        trades = await self.trade_repo.get_all_trades_by_user_id(user_id)

        if not trades:
            raise TradeDoesNotExistError(
                f"There are no trades for user with id {user_id}"
            )

        trade_responses = [TradeResponse.model_validate(trade) for trade in trades]

        return trade_responses

    async def delete(self, trade_public_id: uuid.UUID, user_id: int) -> None:
        trades_deleted = await self.trade_repo.delete_trade_by_public_id_for_user(
            trade_public_id, user_id
        )

        if not trades_deleted:
            raise TradeDoesNotExistError(
                f"There is no trade with public_id {trade_public_id} for user with id {user_id}"
            )

        await self.trade_repo.commit()

    async def update(
        self,
        trade_update_info: TradeUpdateRequest,
        trade_public_id: uuid.UUID,
        user_id: int,
    ) -> TradeResponse:
        trade = await self._get_helper(trade_public_id, user_id)
        trade_update_info_dict = trade_update_info.model_dump(exclude_unset=True)

        await self.trade_repo.update_trade(trade, **trade_update_info_dict)

        await self.trade_repo.commit()

        return TradeResponse.model_validate(trade)


TradeServiceDependency = Annotated[TradeService, Depends(TradeService)]
