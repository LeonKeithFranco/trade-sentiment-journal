import uuid

from fastapi import APIRouter, status

from app.domains.trades.schemas import TradeRequest, TradeResponse
from app.domains.trades.service import TradeServiceDependency
from app.security import CurrentUserDependency

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post("", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def create(
    trade_request: TradeRequest,
    current_user: CurrentUserDependency,
    trade_service: TradeServiceDependency,
) -> TradeResponse:
    return await trade_service.create(trade_request, current_user.id)


@router.get("/{trade_public_id}", response_model=TradeResponse)
async def get(
    trade_public_id: uuid.UUID,
    current_user: CurrentUserDependency,
    trade_service: TradeServiceDependency,
) -> TradeResponse:
    return await trade_service.get(trade_public_id, current_user.id)
