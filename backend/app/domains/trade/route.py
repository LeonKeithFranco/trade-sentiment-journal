from fastapi import APIRouter, status

from app.domains.trade.schemas import TradeRequest, TradeResponse
from app.domains.trade.service import TradeServiceDependency
from app.security import CurrentUserDependency

router = APIRouter(prefix="/trade", tags=["trade"])


@router.post("", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def create(
    trade_request: TradeRequest,
    current_user: CurrentUserDependency,
    trade_service: TradeServiceDependency,
) -> TradeResponse:
    return await trade_service.create(trade_request, current_user.id)
