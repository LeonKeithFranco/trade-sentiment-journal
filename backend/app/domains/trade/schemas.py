import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.core.constants import MAX_TICKER_LENGTH
from app.domains.trade.constants import Direction


class TradeBase(BaseModel):
    ticker: str = Field(
        min_length=1,
        max_length=MAX_TICKER_LENGTH,
    )
    direction: Direction
    position_size: Decimal = Field(
        gt=0,
    )
    entry_price: Decimal = Field(
        gt=0,
    )
    exit_price: Decimal | None = Field(
        default=None,
        gt=0,
    )

    opened_at: AwareDatetime
    closed_at: AwareDatetime | None


class TradeRequest(TradeBase):
    @model_validator(mode="after")
    def validate_exit_price_and_closed_at(self) -> Self:
        exit_price_is_none = self.exit_price is None
        closed_at_is_none = self.closed_at is None
        has_mismatch = exit_price_is_none != closed_at_is_none

        if has_mismatch:
            raise ValueError(
                "exit_price and closed_at must both be None or must both have values"
            )

        return self

    @field_validator("opened_at")
    @classmethod
    def convert_to_utc(cls, v: datetime) -> datetime:
        return v.astimezone(UTC)

    @field_validator("closed_at")
    @classmethod
    def convert_to_utc_if_not_none(cls, v: datetime | None) -> datetime | None:
        return v.astimezone(UTC) if v is not None else None


class TradeResponse(TradeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    public_id: uuid.UUID
    created_on: datetime
    updated_on: datetime
