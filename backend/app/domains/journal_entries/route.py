import uuid

from fastapi import APIRouter, BackgroundTasks, status

from app.domains.journal_entries.schemas import (
    JournalEntryCreateRequest,
    JournalEntryResponse,
    JournalEntryUpdateRequest,
)
from app.domains.journal_entries.service import JournalEntryServiceDependency
from app.domains.nlp.tasks import analyze_and_store_journal_entry_sentiment
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
    """Create a new journal entry and schedule sentiment analysis for it.

    Args:
        journal_entry_create_request: The request body containing the
            journal entry's title, text, and associated trade.
        current_user: The authenticated user making the request.
        journal_entry_service: The injected JournalEntryService instance.
        background_tasks: FastAPI BackgroundTasks instance used to schedule
            the deferred sentiment analysis.

    Returns:
        JournalEntryResponse: The newly created journal entry.
    """
    journal_entry_response = await journal_entry_service.create(
        journal_entry_create_request, current_user.id
    )

    background_tasks.add_task(
        analyze_and_store_journal_entry_sentiment,
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
    """Return all journal entries belonging to the current user.

    Args:
        current_user: The authenticated user making the request.
        journal_entry_service: The injected JournalEntryService instance.

    Returns:
        list[JournalEntryResponse]: All journal entries belonging to the
            current user.
    """
    return await journal_entry_service.get_all(current_user.id)


@router.get("/{journal_entry_public_id}", response_model=JournalEntryResponse)
async def get(
    journal_entry_public_id: uuid.UUID,
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
) -> JournalEntryResponse:
    """Return a single journal entry belonging to the current user.

    Args:
        journal_entry_public_id: The public ID of the journal entry to fetch.
        current_user: The authenticated user making the request.
        journal_entry_service: The injected JournalEntryService instance.

    Returns:
        JournalEntryResponse: The matching journal entry.

    Raises:
        JournalEntryDoesNotExistError: If no journal entry with that public
            ID exists for the current user.
    """
    return await journal_entry_service.get(journal_entry_public_id, current_user.id)


@router.delete("/{journal_entry_public_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    journal_entry_public_id: uuid.UUID,
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
) -> None:
    """Delete a journal entry belonging to the current user.

    Args:
        journal_entry_public_id: The public ID of the journal entry to
            delete.
        current_user: The authenticated user making the request.
        journal_entry_service: The injected JournalEntryService instance.

    Raises:
        JournalEntryDoesNotExistError: If no journal entry with that public
            ID exists for the current user.
    """
    await journal_entry_service.delete(journal_entry_public_id, current_user.id)


@router.patch("/{journal_entry_public_id}", response_model=JournalEntryResponse)
async def update(
    journal_entry_public_id: uuid.UUID,
    journal_entry_update_request: JournalEntryUpdateRequest,
    current_user: CurrentUserDependency,
    journal_entry_service: JournalEntryServiceDependency,
) -> JournalEntryResponse:
    """Update a journal entry belonging to the current user.

    Args:
        journal_entry_public_id: The public ID of the journal entry to
            update.
        journal_entry_update_request: The fields to update on the journal
            entry.
        current_user: The authenticated user making the request.
        journal_entry_service: The injected JournalEntryService instance.

    Returns:
        JournalEntryResponse: The updated journal entry.

    Raises:
        JournalEntryDoesNotExistError: If no journal entry with that public
            ID exists for the current user.
    """
    return await journal_entry_service.update(
        journal_entry_update_request, journal_entry_public_id, current_user.id
    )
