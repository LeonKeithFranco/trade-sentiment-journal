from pydantic import BaseModel, Field

from app.core.constants import MAX_TITLE_LENGTH


class JournalEntryBase(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_TITLE_LENGTH,
    )
    text: str = Field(
        min_length=50,
    )
