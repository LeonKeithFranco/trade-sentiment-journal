import uuid
from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository
from app.models import JournalEntry

type MaybeJournalEntry = JournalEntry | None


class JournalEntryRepository(Repository[JournalEntry]):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def insert_journal_entry(self, **create_info) -> JournalEntry:
        return await self.insert_into_table(JournalEntry, **create_info)

    async def get_journal_entry_by_public_id_for_user(
        self, journal_public_id: uuid.UUID, user_id: int
    ) -> MaybeJournalEntry:
        return await self.get_from_table_by(
            JournalEntry,
            JournalEntry.public_id == journal_public_id,
            JournalEntry.user_id == user_id,
        )

    async def get_all_journal_entries_by_user_id(
        self, user_id: int
    ) -> list[JournalEntry]:
        return await self.get_all_from_table(
            JournalEntry, JournalEntry.user_id == user_id
        )


JournalEntryRepoDependency = Annotated[
    JournalEntryRepository, Depends(JournalEntryRepository)
]
