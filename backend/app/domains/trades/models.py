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
    from app.models import User


class Trade(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "trades"

    __table_args__ = (
        CheckConstraint("direction in ('LONG','SHORT')", name="check_direction"),
        CheckConstraint(
            "closed_at IS NULL OR closed_at >= opened_at",
            name="check_closed_at_After_opened_at",
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
        return Direction(self._direction)

    @direction.setter
    def direction(self, direction: Direction) -> None:
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

    def _update_pnl(self) -> None:
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
    target._update_pnl()


@event.listens_for(Trade, "before_update")
def _receive_before_update(
    _mapper: Mapper[Trade], _connection: Connection, target: Trade
) -> None:
    target._update_pnl()
