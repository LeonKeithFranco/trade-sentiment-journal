import uuid

from fastapi import APIRouter, BackgroundTasks, status

from app.domains.journal_entries.schemas import (
    JournalEntryCreateRequest,
    JournalEntryResponse,
    JournalEntryUpdateRequest,
)
from app.domains.journal_entries.service import JournalEntryServiceDependency
from app.domains.nlp import tasks as nlp_tasks
from app.security import CurrentUserDependency

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])


@router.post(
    "", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED
)
async def create(
    journal_entry_create_request: JournalEntryCreateRequest,
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
    background_tasks: BackgroundTasks,
) -> JournalEntryResponse:
    journal_entry_response = await journal_entry_service.create(
        journal_entry_create_request, current_user.id
    )

    background_tasks.add_task(
        nlp_tasks.inference,
        journal_entry_response.public_id,
        current_user.id,
        journal_entry_response.entry,
    )

    return journal_entry_response


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


@router.patch("/{journal_entry_public_id}", response_model=JournalEntryResponse)
async def update(
    journal_entry_public_id: uuid.UUID,
    journal_entry_update_request: JournalEntryUpdateRequest,
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
) -> JournalEntryResponse:
    return await journal_entry_service.update(
        journal_entry_update_request, journal_entry_public_id, current_user.id
    )
