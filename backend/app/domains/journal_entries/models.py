from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MAX_TITLE_LENGTH
from app.database import Base
from app.database.columns import TradeIDColumn, UserIDColumn
from app.database.mixins import PublicIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models import User


class JournalEntry(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "journal_entries"

    title: Mapped[str | None] = mapped_column(
        String(MAX_TITLE_LENGTH),
    )
    entry: Mapped[str] = mapped_column(
        Text(),
    )

    user_id: Mapped[UserIDColumn]
    trade_id: Mapped[TradeIDColumn]

    user: Mapped["User"] = relationship(
        back_populates="journal_entries",
    )
