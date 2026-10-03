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
    """ORM model representing a registered user.

    Serves as the root entity in the data model, owning a user's refresh
    tokens, trades, and journal entries.

    Attributes:
        id: Auto-incremented primary key inherited from Base.
        public_id: A randomly generated, unique UUID for external references.
        created_on: The UTC timestamp when the row was inserted.
        updated_on: The UTC timestamp when the row was last updated.
        email: The user's unique email address, used for login.
        hashed_password: The user's password, hashed and peppered before storage.
        refresh_tokens: The list of RefreshToken records issued to this user.
        trades: The list of Trade records belonging to this user.
        journal_entries: The list of JournalEntry records belonging to this
            user.
    """

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
    """ORM model representing a JWT refresh token issued to a user.

    Attributes:
        id: Auto-incremented primary key inherited from Base.
        token: The unique refresh token string.
        expires_on: The UTC timestamp after which the token is no longer valid.
        revoked: Whether the token has been explicitly revoked before expiry.
        user_id: The ID of the User this token was issued to.
        user: The associated User record.
    """

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
