from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Connection, DateTime, Numeric, String, event
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship

from app.core.constants import MAX_TICKER_LENGTH
from app.database import Base
from app.database.columns import UserIDColumn
from app.database.mixins import PublicIdMixin, TimestampMixin
from app.domains.trades.constants import Direction

if TYPE_CHECKING:
    from app.models import JournalEntry, User


class Trade(PublicIdMixin, TimestampMixin, Base):
    """ORM model representing a single stock trade.

    Profit and loss is computed automatically from the entry price, exit
    price, position size, and direction whenever the trade is inserted or
    updated with an exit price set.

    Attributes:
        id: Auto-incremented primary key inherited from Base.
        public_id: A randomly generated, unique UUID for external references.
        created_on: The UTC timestamp when the row was inserted.
        updated_on: The UTC timestamp when the row was last updated.
        ticker: The stock's exchange ticker symbol.
        direction: Whether the trade is LONG or SHORT.
        position_size: The number of shares or units traded.
        entry_price: The price per share or unit at which the position was
            opened.
        exit_price: The price per share or unit at which the position was
            closed, or None if the trade is still open.
        profit_and_loss: The realized profit or loss on the trade, or None
            if the trade is still open.
        opened_at: The timestamp at which the trade was opened.
        closed_at: The timestamp at which the trade was closed, or None if
            the trade is still open.
        user_id: The ID of the User who made this trade.
        user: The associated User record.
        journal_entries: The list of JournalEntry records associated with
            this trade.
    """

    __tablename__ = "trades"

    __table_args__ = (
        CheckConstraint("direction in ('LONG','SHORT')", name="check_direction"),
        CheckConstraint(
            "closed_at IS NULL OR closed_at >= opened_at",
            name="check_closed_at_after_opened_at",
        ),
        CheckConstraint(
            "(exit_price IS NULL AND closed_at IS NULL) OR "
            "(exit_price IS NOT NULL AND closed_at IS NOT NULL)",
            name="check_exit_price_and_closed_at_consistency",
        ),
        CheckConstraint(
            "(exit_price IS NULL AND profit_and_loss IS NULL) OR "
            "(exit_price IS NOT NULL AND profit_and_loss IS NOT NULL)",
            name="check_profit_and_loss_consistency",
        ),
    )

    ticker: Mapped[str] = mapped_column(
        String(MAX_TICKER_LENGTH),
        index=True,
    )
    _direction: Mapped[str] = mapped_column(
        String(5),
        name="direction",
    )

    @property
    def direction(self) -> Direction:
        """Get the trade direction as a Direction enum.

        Returns:
            Direction: The parsed direction value.
        """
        return Direction(self._direction)

    @direction.setter
    def direction(self, direction: Direction) -> None:
        """Set the trade direction from a Direction enum.

        Args:
            direction: The direction value to store.
        """
        self._direction = direction.value

    position_size: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )
    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
    )
    exit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
    )
    profit_and_loss: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
    )

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    user_id: Mapped[UserIDColumn]

    user: Mapped["User"] = relationship(
        back_populates="trades",
    )

    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan",
    )

    def _update_pnl(self) -> None:
        """Recompute profit_and_loss from the entry price, exit price, position size, and direction.

        Does nothing if the trade has not been closed (exit_price is None).
        """
        if self.exit_price is None:
            return

        self.profit_and_loss = (
            self.exit_price - self.entry_price
            if self.direction == Direction.LONG
            else self.entry_price - self.exit_price
        ) * self.position_size


@event.listens_for(Trade, "before_insert")
def _receive_before_insert(
    _mapper: Mapper[Trade], _connection: Connection, target: Trade
) -> None:
    """Recompute a trade's profit and loss before it is inserted.

    Registered as a SQLAlchemy "before_insert" event listener for Trade.

    Args:
        _mapper: The SQLAlchemy mapper for Trade, unused.
        _connection: The active database connection, unused.
        target: The Trade instance being inserted.
    """
    target._update_pnl()


@event.listens_for(Trade, "before_update")
def _receive_before_update(
    _mapper: Mapper[Trade], _connection: Connection, target: Trade
) -> None:
    """Recompute a trade's profit and loss before it is updated.

    Registered as a SQLAlchemy "before_update" event listener for Trade.

    Args:
        _mapper: The SQLAlchemy mapper for Trade, unused.
        _connection: The active database connection, unused.
        target: The Trade instance being updated.
    """
    target._update_pnl()
