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
)
from app.domains.trades.service import TradeService, TradeServiceDependency
from app.models import JournalEntry


class JournalEntryService:
    def __init__(
        self,
        journal_entry_repo: JournalEntryRepoDependency,
        trade_service: TradeServiceDependency,
    ) -> None:
        self.journal_entry_repo: JournalEntryRepository = journal_entry_repo
        self.trade_service: TradeService = trade_service

    async def create(
        self,
        journal_entry_create_info: JournalEntryCreateRequest,
        user_id: int,
    ) -> JournalEntryResponse:
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
        journal_entry = await self.get_journal_entry(journal_entry_public_id, user_id)

        return JournalEntryResponse.model_validate(journal_entry)

    async def get_all(self, user_id: int) -> list[JournalEntryResponse]:
        journal_entries = (
            await self.journal_entry_repo.get_all_journal_entries_by_user_id(user_id)
        )

        journal_entry_reponses = [
            JournalEntryResponse.model_validate(journal_entry)
            for journal_entry in journal_entries
        ]

        return journal_entry_reponses


JournalEntryServiceDependency = Annotated[
    JournalEntryService, Depends(JournalEntryService)
]
