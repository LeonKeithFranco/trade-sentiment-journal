from typing import Annotated

from fastapi import Depends

from app.domains.analytics.repository import AnalyticRepoDependency, AnalyticRepository


class AnalyticService:
    def __init__(
        self,
        analytic_repo: AnalyticRepoDependency,
    ) -> None:
        self.trade_repo: AnalyticRepository = analytic_repo


AnalyticServiceDependency = Annotated[AnalyticService, Depends(AnalyticService)]
