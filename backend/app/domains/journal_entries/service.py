from typing import Annotated

from fastapi import Depends

from app.domains.journal_entries.repository import (
    JournalEntryRepoDependency,
    JournalEntryRepository,
)


class JournalEntryService:
    def __init__(
        self,
        journal_entry_repo: JournalEntryRepoDependency,
    ) -> None:
        self.journal_entry_repo: JournalEntryRepository = journal_entry_repo


JournalEntryServiceDependency = Annotated[
    JournalEntryService, Depends(JournalEntryService)
]
