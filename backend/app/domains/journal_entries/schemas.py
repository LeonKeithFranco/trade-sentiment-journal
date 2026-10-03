import uuid

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.core.constants import MAX_TITLE_LENGTH


class JournalEntryBase(BaseModel):
    """Base schema for journal entry requests and responses.

    Attributes:
        title: An optional short title for the journal entry.
        entry: The full text content of the journal entry.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_TITLE_LENGTH,
    )
    entry: str = Field(
        min_length=50,
        max_length=4096,
    )


class JournalEntryCreateRequest(JournalEntryBase):
    """Pydantic request model for the POST /journal-entries endpoint.

    Attributes:
        trade_public_id: The public ID of the trade this journal entry is
            about.
    """

    trade_public_id: uuid.UUID


class JournalEntryUpdateRequest(BaseModel):
    """Pydantic request model for the PATCH /journal-entries/{id} endpoint.

    All fields are optional; only the fields provided are updated.

    Attributes:
        title: The journal entry's new title, or None to leave unchanged.
        entry: The journal entry's new text content, or None to leave
            unchanged.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_TITLE_LENGTH,
    )
    entry: str | None = Field(
        default=None,
        min_length=50,
        max_length=4096,
    )


class JournalEntryResponse(JournalEntryBase):
    """Pydantic response model for journal entry endpoints.

    Attributes:
        public_id: The journal entry's public-facing UUID.
        created_on: The UTC timestamp when the journal entry was created.
        updated_on: The UTC timestamp when the journal entry was last
            updated.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    public_id: uuid.UUID
    created_on: AwareDatetime
    updated_on: AwareDatetime
