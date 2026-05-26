import uuid
from datetime import UTC
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
from app.domains.trades.constants import Direction


class TradeBase(BaseModel):
    ticker: str = Field(
        min_length=1,
        max_length=MAX_TICKER_LENGTH,
    )
    direction: Direction
    position_size: Decimal = Field(
        gt=0,
        examples=[1.000],
    )
    entry_price: Decimal = Field(
        gt=0,
        examples=[123.45],
    )
    exit_price: Decimal | None = Field(
        default=None,
        gt=0,
        examples=[500.55],
    )

    opened_at: AwareDatetime
    closed_at: AwareDatetime | None = None


class TradeCreateRequest(TradeBase):
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

    @model_validator(mode="after")
    def validate_closed_at_later_than_opened_at(self) -> Self:
        if (self.closed_at is not None) and (self.opened_at > self.closed_at):
            raise ValueError("closed_at should be later than opened_at")

        return self

    @field_validator("opened_at")
    @classmethod
    def convert_to_utc(cls, v: AwareDatetime) -> AwareDatetime:
        return v.astimezone(UTC)

    @field_validator("closed_at")
    @classmethod
    def convert_to_utc_if_not_none(
        cls, v: AwareDatetime | None
    ) -> AwareDatetime | None:
        return v.astimezone(UTC) if v is not None else None


class TradeUpdateRequest(BaseModel):
    ticker: str | None = Field(
        default=None,
        min_length=1,
        max_length=MAX_TICKER_LENGTH,
    )
    direction: Direction | None = None
    position_size: Decimal | None = Field(
        default=None,
        gt=0,
        examples=[1.000],
    )
    entry_price: Decimal | None = Field(
        default=None,
        gt=0,
        examples=[123.45],
    )
    exit_price: Decimal | None = Field(
        default=None,
        gt=0,
        examples=[500.55],
    )

    opened_at: AwareDatetime | None = None
    closed_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def validate_closed_at_later_than_opened_at(self) -> Self:
        if (
            (self.opened_at is not None)
            and (self.closed_at is not None)
            and (self.opened_at > self.closed_at)
        ):
            raise ValueError("closed_at should be later than opened_at")

        return self

    @field_validator("opened_at", "closed_at")
    @classmethod
    def convert_to_utc_if_not_none(
        cls, v: AwareDatetime | None
    ) -> AwareDatetime | None:
        return v.astimezone(UTC) if v is not None else None


class TradeResponse(TradeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    profit_and_loss: Decimal | None = Field(None, examples=[6.70])

    public_id: uuid.UUID
    created_on: AwareDatetime
    updated_on: AwareDatetime
