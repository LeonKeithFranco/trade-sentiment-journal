from typing import cast

from sqlalchemy import ColumnElement, CursorResult, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.database import Base


class Repository[T: Base]:
    """Generic data-access layer providing common CRUD operations for ORM models.

    Intended to be subclasses by domain-speicfic repositories, which wrap the generic
    operations with model-specific, sematically named methods. The type parameter T is the
    specific ORM model (a subclass of Base) that a given repository instance operates on.
    Callers are responsible for committing the session via the commit method after writes.

    Attributes:
        db: The underlying async SQLAlchemy session.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the repository with a database session.

        Args:
            db: An async SQLAlchemy session.
        """
        self.db: AsyncSession = db

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.db.commit()

    async def insert_into_table(self, model: type[T], **create_info) -> T:
        """Insert a new record into the table for the given model.

        Constructs a new isntance of the model, sets the provided attributes, and flushes
        it to the database so generated values (e.g. primary keys, defautls) are
        available.

        Args:
            model: The ORM model class to insert a record for.
            **create_info: Column values to set on the new record.

        Returns:
            T: The newly created and refreshed record.
        """
        record = model()

        for key, val in create_info.items():
            setattr(record, key, val)

        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)

        return record

    async def get_from_table_by(
        self,
        model: type[T],
        *where_clauses: ColumnElement[bool],
        options: list[ExecutableOption] | None = None,
    ) -> T | None:
        """Fetch a single record from the table matching the given clauses.

        Args:
            model: The ORM model class to query.
            *where_clauses: SQLAlchemy filter conditions to apply.
            options: Optional SQLAlchemy loader options (e.g. eager loading) to apply to
                the query.

        Returns:
            T: The matching record, or None if no record matches.
        """
        query = select(model).where(*where_clauses)
        if options:
            query = query.options(*options)
        results = await self.db.execute(query)

        return results.scalar_one_or_none()

    async def get_all_from_table(
        self, model: type[T], *where_clauses: ColumnElement[bool]
    ) -> list[T]:
        """Fetch all records from the table matching the given clauses.

        Args:
            model: The ORM model class to query.
            *where_clauses: SQLAlchemy filter conditinos to apply.

        Returns:
            list[T]: All matching records.
        """
        query = select(model).where(*where_clauses)
        results = await self.db.execute(query)

        return list(results.scalars().all())

    async def delete_from_table_by(
        self, model: type[T], *where_clauses: ColumnElement[bool]
    ) -> int:
        """Delete records from the table matching the given clauses.

        Args:
            model: The ORM model class to delete records from.
            *where_clauses: SQLAlchemy filter conditions to apply.

        Returns:
            int: The number of rows deleted.
        """
        query = delete(model).where(*where_clauses)
        results = cast(CursorResult, await self.db.execute(query))

        return results.rowcount

    async def update_record(self, record: T, **update_info) -> T:
        """Update an existing record's attributes and persist the change.

        Args:
            records: The ORM instance to update.
            **update_info: Column values to set on the record.

        Returns:
            T: The updated and refreshed record.
        """
        for key, val in update_info.items():
            setattr(record, key, val)

        await self.db.flush()
        await self.db.refresh(record)

        return record
