from typing import Annotated

from fastapi import Depends

from app.domains.auth.repository import UserRepoDependency, UserRepository
from app.domains.trade.repository import TradeRepoDependency, TradeRepository


class TradeService:
    def __init__(
        self,
        user_repo: UserRepoDependency,
        trade_repo: TradeRepoDependency,
    ) -> None:
        self.user_repo: UserRepository = user_repo
        self.trade_repo: TradeRepository = trade_repo


TradeServiceDependency = Annotated[TradeService, Depends(TradeService)]
