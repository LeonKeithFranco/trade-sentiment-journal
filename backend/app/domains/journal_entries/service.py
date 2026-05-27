from typing import Annotated

from fastapi import Depends

from app.domains.journal_entries.repository import (
    JournalEntryRepoDependency,
    JournalEntryRepository,
)
from app.domains.journal_entries.schemas import (
    JournalEntryCreateRequest,
    JournalEntryResponse,
)


class JournalEntryService:
    def __init__(
        self,
        journal_entry_repo: JournalEntryRepoDependency,
    ) -> None:
        self.journal_entry_repo: JournalEntryRepository = journal_entry_repo

    async def create(
        self,
        journal_entry_create_info: JournalEntryCreateRequest,
        user_id: int,
        trade_id: int,
    ) -> JournalEntryResponse:
        journal_entry_create_info_dict = journal_entry_create_info.model_dump(
            exclude_unset=True
        )
        journal_entry_create_info_dict.pop("trade_public_id")

        new_journal_entry = await self.journal_entry_repo.insert_journal_entry(
            user_id=user_id, trade_id=trade_id, **journal_entry_create_info_dict
        )

        await self.journal_entry_repo.commit()

        return JournalEntryResponse.model_validate(new_journal_entry)


JournalEntryServiceDependency = Annotated[
    JournalEntryService, Depends(JournalEntryService)
]
