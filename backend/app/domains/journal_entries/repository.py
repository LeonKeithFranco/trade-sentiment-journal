from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository


class JournalEntryRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)


JournalEntryRepoDependency = Annotated[
    JournalEntryRepository, Depends(JournalEntryRepository)
]
