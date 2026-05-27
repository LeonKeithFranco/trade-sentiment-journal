import uuid

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.core.constants import MAX_TITLE_LENGTH


class JournalEntryBase(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_TITLE_LENGTH,
    )
    entry: str = Field(
        min_length=50,
    )


class JournalEntryCreateRequest(JournalEntryBase):
    trade_public_id: uuid.UUID


class JournalEntryResponse(JournalEntryBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    public_id: uuid.UUID
    created_on: AwareDatetime
    updated_on: AwareDatetime
