from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(256),
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(256),
    )
