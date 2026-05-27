from typing import cast

from sqlalchemy import ColumnElement, CursorResult, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.database import Base


class Repository[T: Base]:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def commit(self) -> None:
        await self.db.commit()

    async def insert_into_table(self, model: type[T], **create_info) -> T:
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
        query = select(model).where(*where_clauses)
        if options:
            query = query.options(*options)
        results = await self.db.execute(query)

        return results.scalar_one_or_none()

    async def get_all_from_table(
        self, model: type[T], *where_clauses: ColumnElement[bool]
    ) -> list[T]:
        query = select(model).where(*where_clauses)
        results = await self.db.execute(query)

        return list(results.scalars().all())

    async def delete_from_table_by(
        self, model: type[T], *where_clauses: ColumnElement[bool]
    ) -> int:
        query = delete(model).where(*where_clauses)
        results = cast(CursorResult, await self.db.execute(query))

        return results.rowcount

    async def update_record(self, record: T, **update_info) -> T:
        for key, val in update_info.items():
            setattr(record, key, val)

        await self.db.flush()
        await self.db.refresh(record)

        return record
