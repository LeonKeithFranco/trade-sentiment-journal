import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class PublicIdMixin:
    """Mixin adding a public-facing UUID identifier to a model.

    Intended for models whose internal integer primary key should not be exposed
    externally.

    Attributes:
        public_id: A randomly generated, unique UUID for external references.
    """

    public_id: Mapped[uuid.UUID] = mapped_column(
        unique=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """Mixin adding creation and last-updated timestamps to a model.

    Attributes:
        created_on: The UTC timestamp when the row was inserted, set by the database.
        updated_on: The UTC timestamp when the row was last updated, set by the database
            and refreshed automatically on update.
    """

    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
