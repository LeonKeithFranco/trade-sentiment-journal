from fastapi import APIRouter, status

from app.domains.journal_entries.schemas import (
    JournalEntryCreateRequest,
    JournalEntryResponse,
)
from app.domains.journal_entries.service import JournalEntryServiceDependency
from app.security import CurrentUserDependency

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])


@router.post(
    "", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    journal_entry_create_request: JournalEntryCreateRequest,
    current_user: CurrentUserDependency,
    journal_entry_serivce: JournalEntryServiceDependency,
) -> JournalEntryResponse:
    return await journal_entry_serivce.create(
        journal_entry_create_request, current_user.id
    )
