import uuid

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
    journal_entry_service: JournalEntryServiceDependency,
) -> JournalEntryResponse:
    return await journal_entry_service.create(
        journal_entry_create_request, current_user.id
    )


@router.get("", response_model=list[JournalEntryResponse])
async def get_all(
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
) -> list[JournalEntryResponse]:
    return await journal_entry_service.get_all(current_user.id)


@router.get("/{journal_entry_public_id}", response_model=JournalEntryResponse)
async def get(
    journal_entry_public_id: uuid.UUID,
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
) -> JournalEntryResponse:
    return await journal_entry_service.get(journal_entry_public_id, current_user.id)


@router.delete("/{journal_entry_public_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    journal_entry_public_id: uuid.UUID,
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
) -> None:
    await journal_entry_service.delete(journal_entry_public_id, current_user.id)
