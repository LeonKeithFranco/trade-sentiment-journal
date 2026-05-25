from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.database.columns import UserIDColumn
from app.database.mixins import PublicIdMixin, TimestampMixin
from app.domains.trade.constants import Direction

if TYPE_CHECKING:
    from app.models import User


class Trade(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "trades"

    __table_args__ = (
        CheckConstraint("direction in ('LONG','SHORT')", name="check_direction"),
    )

    ticker: Mapped[str] = mapped_column(
        String(10),
        index=True,
    )
    direction: Mapped[str] = mapped_column(
        String(5),
    )

    @property
    def direction_(self) -> Direction:
        return Direction(self.direction)

    @direction_.setter
    def direction_(self, direction: Direction) -> None:
        self.direction = direction.value

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
