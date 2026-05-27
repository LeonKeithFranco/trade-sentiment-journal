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
from app.domains.trades.service import TradeService, TradeServiceDependency


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


JournalEntryServiceDependency = Annotated[
    JournalEntryService, Depends(JournalEntryService)
]
