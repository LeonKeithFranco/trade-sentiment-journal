import uuid

from fastapi import APIRouter, status

from app.domains.trades.schemas import (
    TradeCreateRequest,
    TradeResponse,
    TradeUpdateRequest,
)
from app.domains.trades.service import TradeServiceDependency
from app.security import CurrentUserDependency

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post("", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def create(
    trade_request: TradeCreateRequest,
    current_user: CurrentUserDependency,
    trade_service: TradeServiceDependency,
) -> TradeResponse:
    """Create a new trade for the current user.

    Args:
        trade_request: The request body containing the trade's details.
        current_user: The authenticated user making the request.
        trade_service: The injected TradeService instance.

    Returns:
        TradeResponse: The newly created trade.
    """
    return await trade_service.create(trade_request, current_user.id)


@router.get("", response_model=list[TradeResponse])
async def get_all(
    current_user: CurrentUserDependency, trade_service: TradeServiceDependency
) -> list[TradeResponse]:
    """Return all trades belonging to the current user.

    Args:
        current_user: The authenticated user making the request.
        trade_service: The injected TradeService instance.

    Returns:
        list[TradeResponse]: All trades belonging to the current user.
    """
    return await trade_service.get_all(current_user.id)


@router.get("/{trade_public_id}", response_model=TradeResponse)
async def get(
    trade_public_id: uuid.UUID,
    current_user: CurrentUserDependency,
    trade_service: TradeServiceDependency,
) -> TradeResponse:
    """Return a single trade belonging to the current user.

    Args:
        trade_public_id: The public ID of the trade to fetch.
        current_user: The authenticated user making the request.
        trade_service: The injected TradeService instance.

    Returns:
        TradeResponse: The matching trade.

    Raises:
        TradeDoesNotExistError: If no trade with that public ID exists for
            the current user.
    """
    return await trade_service.get(trade_public_id, current_user.id)


@router.delete("/{trade_public_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    trade_public_id: uuid.UUID,
    current_user: CurrentUserDependency,
    trade_service: TradeServiceDependency,
) -> None:
    """Delete a trade belonging to the current user.

    Args:
        trade_public_id: The public ID of the trade to delete.
        current_user: The authenticated user making the request.
        trade_service: The injected TradeService instance.

    Raises:
        TradeDoesNotExistError: If no trade with that public ID exists for
            the current user.
    """
    await trade_service.delete(trade_public_id, current_user.id)


@router.patch("/{trade_public_id}", response_model=TradeResponse)
async def update(
    trade_public_id: uuid.UUID,
    trade_update_request: TradeUpdateRequest,
    current_user: CurrentUserDependency,
    trade_service: TradeServiceDependency,
) -> TradeResponse:
    """Update a trade belonging to the current user.

    Args:
        trade_public_id: The public ID of the trade to update.
        trade_update_request: The fields to update on the trade.
        current_user: The authenticated user making the request.
        trade_service: The injected TradeService instance.

    Returns:
        TradeResponse: The updated trade.

    Raises:
        TradeDoesNotExistError: If no trade with that public ID exists for
            the current user.
        ClosedAtBeforeOpenedAtError: If the update would set closed_at
            earlier than opened_at.
        TradeClosedFieldsMismatchError: If the update would leave exit_price
            and closed_at inconsistent (one set without the other).
    """
    return await trade_service.update(
        trade_update_request, trade_public_id, current_user.id
    )
