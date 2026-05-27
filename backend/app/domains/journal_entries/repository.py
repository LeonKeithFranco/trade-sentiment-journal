from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository
from app.models import JournalEntry


class JournalEntryRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def insert_journal_entry(
        self, user_id: int, trade_id: int, **create_info
    ) -> JournalEntry:
        journal_entry = JournalEntry()
        journal_entry.user_id = user_id
        journal_entry.trade_id = trade_id

        for key, val in create_info.items():
            setattr(journal_entry, key, val)

        self.db.add(journal_entry)
        await self.db.flush()
        await self.db.refresh(journal_entry)

        return journal_entry


JournalEntryRepoDependency = Annotated[
    JournalEntryRepository, Depends(JournalEntryRepository)
]
