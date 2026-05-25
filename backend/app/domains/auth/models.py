from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.database.columns import UserIDColumn
from app.database.mixins import PublicIdMixin, TimestampMixin


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
    user_id: UserIDColumn

    user: Mapped["User"] = relationship(
        back_populates="refresh_tokens",
    )
