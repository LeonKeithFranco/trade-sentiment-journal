from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.database.columns import UserIDColumn
from app.database.mixins import PublicIdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models import JournalEntry, Trade


class User(PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(256),
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(256),
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    trades: Mapped[list["Trade"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(
        unique=True,
    )
    expires_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    revoked: Mapped[bool] = mapped_column(
        default=False,
        index=True,
    )
    user_id: Mapped[UserIDColumn]

    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens",
    )
