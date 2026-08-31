import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from app.domains.trades.exceptions import (
    ClosedAtBeforeOpenedAtError,
    TradeClosedFieldsMismatchError,
    TradeDoesNotExistError,
)
from app.domains.trades.repository import TradeRepoDependency, TradeRepository
from app.domains.trades.schemas import (
    TradeCreateRequest,
    TradeResponse,
    TradeUpdateRequest,
)
from app.models import Trade


class TradeService:
    """Service layer for creating and managing trades.

    Attributes:
        trade_repo: The repository used for trade database access.
    """

    def __init__(
        self,
        trade_repo: TradeRepoDependency,
    ) -> None:
        """Initialize the service with an injected trade repository.

        Args:
            trade_repo: The TradeRepository instance, provided by FastAPI's
                dependency injection.
        """
        self.trade_repo: TradeRepository = trade_repo

    async def get_trade(self, trade_public_id: uuid.UUID, user_id: int) -> Trade:
        """Fetch the ORM Trade for a user, raising if it does not exist.

        Args:
            trade_public_id: The public ID of the trade to fetch.
            user_id: The ID of the user the trade must belong to.

        Returns:
            Trade: The matching trade.

        Raises:
            TradeDoesNotExistError: If no trade with that public ID exists
                for the user.
        """
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
        """Create a new trade for a user.

        Args:
            trade_info: The trade's details.
            user_id: The ID of the user creating the trade.

        Returns:
            TradeResponse: The newly created trade.
        """
        trade_info_dict = trade_info.model_dump(exclude_unset=True)

        new_trade = await self.trade_repo.insert_trade(
            user_id=user_id, **trade_info_dict
        )

        await self.trade_repo.commit()

        return TradeResponse.model_validate(new_trade)

    async def get(self, trade_public_id: uuid.UUID, user_id: int) -> TradeResponse:
        """Fetch a single trade belonging to a user.

        Args:
            trade_public_id: The public ID of the trade to fetch.
            user_id: The ID of the user the trade must belong to.

        Returns:
            TradeResponse: The matching trade.

        Raises:
            TradeDoesNotExistError: If no trade with that public ID exists
                for the user.
        """
        trade = await self.get_trade(trade_public_id, user_id)

        return TradeResponse.model_validate(trade)

    async def get_all(self, user_id: int) -> list[TradeResponse]:
        """Fetch all trades belonging to a user.

        Args:
            user_id: The ID of the user whose trades to fetch.

        Returns:
            list[TradeResponse]: All trades belonging to the user.
        """
        trades = await self.trade_repo.get_all_trades_by_user_id(user_id)

        trade_responses = [TradeResponse.model_validate(trade) for trade in trades]

        return trade_responses

    async def delete(self, trade_public_id: uuid.UUID, user_id: int) -> None:
        """Delete a trade belonging to a user.

        Args:
            trade_public_id: The public ID of the trade to delete.
            user_id: The ID of the user the trade must belong to.

        Raises:
            TradeDoesNotExistError: If no trade with that public ID exists
                for the user.
        """
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
        """Update a trade belonging to a user.

        Only the fields set on trade_update_info are changed. Database check
        constraint violations arising from the update are translated into
        domain-specific exceptions.

        Args:
            trade_update_info: The fields to update on the trade.
            trade_public_id: The public ID of the trade to update.
            user_id: The ID of the user the trade must belong to.

        Returns:
            TradeResponse: The updated trade.

        Raises:
            TradeDoesNotExistError: If no trade with that public ID exists
                for the user.
            ClosedAtBeforeOpenedAtError: If the update would set closed_at
                earlier than opened_at.
            TradeClosedFieldsMismatchError: If the update would leave
                exit_price and closed_at inconsistent (one set without the
                other).
        """
        trade = await self.get_trade(trade_public_id, user_id)
        trade_update_info_dict = trade_update_info.model_dump(exclude_unset=True)

        try:
            updated_trade = await self.trade_repo.update_trade(
                trade, **trade_update_info_dict
            )
        except IntegrityError as exc:
            cause = getattr(exc.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)

            match constraint:
                case "check_closed_at_after_opened_at":
                    raise ClosedAtBeforeOpenedAtError
                case "check_exit_price_and_closed_at_consistency":
                    raise TradeClosedFieldsMismatchError
                case _:
                    raise

        await self.trade_repo.commit()

        return TradeResponse.model_validate(updated_trade)


TradeServiceDependency = Annotated[TradeService, Depends(TradeService)]
