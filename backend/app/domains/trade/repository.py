from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository


class TradeRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)


TradeRepoDependency = Annotated[TradeRepository, Depends(TradeRepository)]
