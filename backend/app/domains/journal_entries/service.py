import uuid
from typing import Annotated

from fastapi import Depends

from app.domains.journal_entries.exceptions import JournalEntryDoesNotExistError
from app.domains.journal_entries.repository import (
    JournalEntryRepoDependency,
    JournalEntryRepository,
)
from app.domains.journal_entries.schemas import (
    JournalEntryCreateRequest,
    JournalEntryResponse,
    JournalEntryUpdateRequest,
)
from app.domains.trades.service import TradeService, TradeServiceDependency
from app.models import JournalEntry


class JournalEntryService:
    """Service layer for creating and managing journal entries.

    Attributes:
        journal_entry_repo: The repository used for journal entry database
            access.
        trade_service: The service used to validate and look up associated
            trades.
    """

    def __init__(
        self,
        journal_entry_repo: JournalEntryRepoDependency,
        trade_service: TradeServiceDependency,
    ) -> None:
        """Initialize the service with injected journal entry repository and trade service.

        Args:
            journal_entry_repo: The JournalEntryRepository instance, provided
                by FastAPI's dependency injection.
            trade_service: The TradeService instance, provided by FastAPI's
                dependency injection.
        """
        self.journal_entry_repo: JournalEntryRepository = journal_entry_repo
        self.trade_service: TradeService = trade_service

    async def create(
        self,
        journal_entry_create_info: JournalEntryCreateRequest,
        user_id: int,
    ) -> JournalEntryResponse:
        """Create a new journal entry for a user's trade.

        Verifies the referenced trade exists and belongs to the user before
        creating the journal entry.

        Args:
            journal_entry_create_info: The journal entry's title, text, and
                associated trade's public ID.
            user_id: The ID of the user creating the journal entry.

        Returns:
            JournalEntryResponse: The newly created journal entry.

        Raises:
            TradeDoesNotExistError: If the referenced trade does not exist
                for the user.
        """
        trade = await self.trade_service.get_trade(
            journal_entry_create_info.trade_public_id, user_id
        )

        journal_entry_create_info_dict = journal_entry_create_info.model_dump(
            exclude_unset=True
        )
        journal_entry_create_info_dict.pop("trade_public_id")

        new_journal_entry = await self.journal_entry_repo.insert_journal_entry(
            user_id=user_id, trade_id=trade.id, **journal_entry_create_info_dict
        )

        await self.journal_entry_repo.commit()

        return JournalEntryResponse.model_validate(new_journal_entry)

    async def get_journal_entry(
        self, journal_entry_public_id: uuid.UUID, user_id: int
    ) -> JournalEntry:
        """Fetch the ORM JournalEntry for a user, raising if it does not exist.

        Args:
            journal_entry_public_id: The public ID of the journal entry to
                fetch.
            user_id: The ID of the user the journal entry must belong to.

        Returns:
            JournalEntry: The matching journal entry.

        Raises:
            JournalEntryDoesNotExistError: If no journal entry with that
                public ID exists for the user.
        """
        journal_entry = (
            await self.journal_entry_repo.get_journal_entry_by_public_id_for_user(
                journal_entry_public_id, user_id
            )
        )

        if journal_entry is None:
            raise JournalEntryDoesNotExistError(
                f"There is no journal entry with public_id {journal_entry_public_id} for user with id {user_id}"
            )

        return journal_entry

    async def get(
        self, journal_entry_public_id: uuid.UUID, user_id: int
    ) -> JournalEntryResponse:
        """Fetch a single journal entry belonging to a user.

        Args:
            journal_entry_public_id: The public ID of the journal entry to
                fetch.
            user_id: The ID of the user the journal entry must belong to.

        Returns:
            JournalEntryResponse: The matching journal entry.

        Raises:
            JournalEntryDoesNotExistError: If no journal entry with that
                public ID exists for the user.
        """
        journal_entry = await self.get_journal_entry(journal_entry_public_id, user_id)

        return JournalEntryResponse.model_validate(journal_entry)

    async def get_all(self, user_id: int) -> list[JournalEntryResponse]:
        """Fetch all journal entries belonging to a user.

        Args:
            user_id: The ID of the user whose journal entries to fetch.

        Returns:
            list[JournalEntryResponse]: All journal entries belonging to the
                user.
        """
        journal_entries = (
            await self.journal_entry_repo.get_all_journal_entries_by_user_id(user_id)
        )

        journal_entry_responses = [
            JournalEntryResponse.model_validate(journal_entry)
            for journal_entry in journal_entries
        ]

        return journal_entry_responses

    async def delete(self, journal_entry_public_id: uuid.UUID, user_id: int) -> None:
        """Delete a journal entry belonging to a user.

        Args:
            journal_entry_public_id: The public ID of the journal entry to
                delete.
            user_id: The ID of the user the journal entry must belong to.

        Raises:
            JournalEntryDoesNotExistError: If no journal entry with that
                public ID exists for the user.
        """
        journal_entries_deleted = (
            await self.journal_entry_repo.delete_journal_entry_by_public_id_for_user(
                journal_entry_public_id, user_id
            )
        )

        if not journal_entries_deleted:
            raise JournalEntryDoesNotExistError(
                f"There is no journal entry with public_id {journal_entry_public_id} for user with id {user_id}"
            )

        await self.journal_entry_repo.commit()

    async def update(
        self,
        journal_entry_update_info: JournalEntryUpdateRequest,
        journal_entry_public_id: uuid.UUID,
        user_id: int,
    ) -> JournalEntryResponse:
        """Update a journal entry belonging to a user.

        Only the fields set on journal_entry_update_info are changed.

        Args:
            journal_entry_update_info: The fields to update on the journal
                entry.
            journal_entry_public_id: The public ID of the journal entry to
                update.
            user_id: The ID of the user the journal entry must belong to.

        Returns:
            JournalEntryResponse: The updated journal entry.

        Raises:
            JournalEntryDoesNotExistError: If no journal entry with that
                public ID exists for the user.
        """
        journal_entry = await self.get_journal_entry(journal_entry_public_id, user_id)
        journal_entry_update_info_dict = journal_entry_update_info.model_dump(
            exclude_unset=True
        )

        updated_journal_entry = await self.journal_entry_repo.update_journal_entry(
            journal_entry, **journal_entry_update_info_dict
        )

        await self.journal_entry_repo.commit()

        return JournalEntryResponse.model_validate(updated_journal_entry)


JournalEntryServiceDependency = Annotated[
    JournalEntryService, Depends(JournalEntryService)
]
