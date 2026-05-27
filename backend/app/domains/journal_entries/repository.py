import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.database import DbDependency
from app.database.repository import Repository
from app.models import JournalEntry

type MaybeJournalEntry = JournalEntry | None


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

    async def get_journal_entry_by_public_id_for_user(
        self, trade_public_id: uuid.UUID, user_id: int
    ) -> MaybeJournalEntry:
        query = (
            select(JournalEntry)
            .where(JournalEntry.public_id == trade_public_id)
            .where(JournalEntry.user_id == user_id)
        )
        results = await self.db.execute(query)
        journal_entry = results.scalar_one_or_none()

        return journal_entry


JournalEntryRepoDependency = Annotated[
    JournalEntryRepository, Depends(JournalEntryRepository)
]
