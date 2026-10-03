import uuid
from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository
from app.models import JournalEntry

type MaybeJournalEntry = JournalEntry | None


class JournalEntryRepository(Repository[JournalEntry]):
    """Data-access layer for JournalEntry records.

    Attributes:
        db: The underlying async SQLAlchemy session.
    """

    def __init__(self, db: DbDependency) -> None:
        """Initialize the repository with a database session.

        Args:
            db: An async SQLAlchemy session, provided by FastAPI's dependency
                injection via get_db.
        """
        super().__init__(db)

    async def insert_journal_entry(self, **create_info) -> JournalEntry:
        """Create a new journal entry record.

        Args:
            **create_info: Column values to set on the new journal entry.

        Returns:
            JournalEntry: The newly created journal entry.
        """
        return await self.insert_into_table(JournalEntry, **create_info)

    async def get_journal_entry_by_public_id_for_user(
        self, journal_public_id: uuid.UUID, user_id: int
    ) -> MaybeJournalEntry:
        """Look up a journal entry by public ID, scoped to a specific user.

        Args:
            journal_public_id: The public UUID of the journal entry to
                search for.
            user_id: The ID of the user the journal entry must belong to.

        Returns:
            JournalEntry: The matching journal entry, or None if no journal
                entry with that public ID exists for the user.
        """
        return await self.get_from_table_by(
            JournalEntry,
            JournalEntry.public_id == journal_public_id,
            JournalEntry.user_id == user_id,
        )

    async def get_all_journal_entries_by_user_id(
        self, user_id: int
    ) -> list[JournalEntry]:
        """Fetch all journal entries belonging to a user.

        Args:
            user_id: The ID of the user whose journal entries to fetch.

        Returns:
            list[JournalEntry]: All journal entries belonging to the user.
        """
        return await self.get_all_from_table(
            JournalEntry, JournalEntry.user_id == user_id
        )

    async def delete_journal_entry_by_public_id_for_user(
        self, journal_entry_public_id: uuid.UUID, user_id: int
    ) -> int:
        """Delete a journal entry by public ID, scoped to a specific user.

        Args:
            journal_entry_public_id: The public UUID of the journal entry to
                delete.
            user_id: The ID of the user the journal entry must belong to.

        Returns:
            int: The number of rows deleted (0 or 1).
        """
        return await self.delete_from_table_by(
            JournalEntry,
            JournalEntry.public_id == journal_entry_public_id,
            JournalEntry.user_id == user_id,
        )

    async def update_journal_entry(
        self,
        journal_entry: JournalEntry,
        **update_info,
    ) -> JournalEntry:
        """Update an existing journal entry's attributes and persist the change.

        Args:
            journal_entry: The journal entry instance to update.
            **update_info: Column values to set on the journal entry.

        Returns:
            JournalEntry: The updated journal entry.
        """
        return await self.update_record(journal_entry, **update_info)


JournalEntryRepoDependency = Annotated[
    JournalEntryRepository, Depends(JournalEntryRepository)
]
