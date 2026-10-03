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
    """Base schema for trade-related requests and responses.

    Attributes:
        ticker: The stock's exchange ticker symbol.
        direction: Whether the trade is LONG or SHORT.
        position_size: The number of shares or units traded.
        entry_price: The price per share or unit at which the position was
            opened.
        exit_price: The price per share or unit at which the position was
            closed, or None if the trade is still open.
        opened_at: The timestamp at which the trade was opened.
        closed_at: The timestamp at which the trade was closed, or None if
            the trade is still open.
    """

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
    """Pydantic request model for the POST /trades endpoint."""

    @model_validator(mode="after")
    def validate_exit_price_and_closed_at(self) -> Self:
        """Validate that exit_price and closed_at are both set or both unset.

        Returns:
            Self: The validated model, unchanged.

        Raises:
            ValueError: If exactly one of exit_price and closed_at is set.
        """
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
        """Validate that closed_at, if set, is not earlier than opened_at.

        Returns:
            Self: The validated model, unchanged.

        Raises:
            ValueError: If closed_at is set and earlier than opened_at.
        """
        if (self.closed_at is not None) and (self.opened_at > self.closed_at):
            raise ValueError("closed_at should be later than opened_at")

        return self

    @field_validator("opened_at")
    @classmethod
    def convert_to_utc(cls, v: AwareDatetime) -> AwareDatetime:
        """Convert opened_at to UTC.

        Args:
            v: The timezone-aware datetime to convert.

        Returns:
            AwareDatetime: The datetime converted to UTC.
        """
        return v.astimezone(UTC)

    @field_validator("closed_at")
    @classmethod
    def convert_to_utc_if_not_none(
        cls, v: AwareDatetime | None
    ) -> AwareDatetime | None:
        """Convert closed_at to UTC if it is set.

        Args:
            v: The timezone-aware datetime to convert, or None.

        Returns:
            AwareDatetime: The datetime converted to UTC, or None if v was
                None.
        """
        return v.astimezone(UTC) if v is not None else None


class TradeUpdateRequest(BaseModel):
    """Pydantic request model for the PATCH /trades/{id} endpoint.

    All fields are optional; only the fields provided are updated.

    Attributes:
        ticker: The trade's new ticker symbol, or None to leave unchanged.
        direction: The trade's new direction, or None to leave unchanged.
        position_size: The trade's new position size, or None to leave
            unchanged.
        entry_price: The trade's new entry price, or None to leave unchanged.
        exit_price: The trade's new exit price, or None to leave unchanged.
        opened_at: The trade's new opened_at timestamp, or None to leave
            unchanged.
        closed_at: The trade's new closed_at timestamp, or None to leave
            unchanged.
    """

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
        """Validate that closed_at, if set, is not earlier than opened_at.

        Only applies when both opened_at and closed_at are provided in the
        update.

        Returns:
            Self: The validated model, unchanged.

        Raises:
            ValueError: If both are set and closed_at is earlier than
                opened_at.
        """
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
        """Convert opened_at or closed_at to UTC if set.

        Args:
            v: The timezone-aware datetime to convert, or None.

        Returns:
            AwareDatetime: The datetime converted to UTC, or None if v was
                None.
        """
        return v.astimezone(UTC) if v is not None else None


class TradeResponse(TradeBase):
    """Pydantic response model for trade-related endpoints.

    Attributes:
        profit_and_loss: The realized profit or loss on the trade, or None
            if the trade is still open.
        public_id: The trade's public-facing UUID.
        created_on: The UTC timestamp when the trade was created.
        updated_on: The UTC timestamp when the trade was last updated.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    profit_and_loss: Decimal | None = Field(None, examples=[6.70])

    public_id: uuid.UUID
    created_on: AwareDatetime
    updated_on: AwareDatetime
