from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base


class Repository[T: Base]:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def commit(self) -> None:
        await self.db.commit()

    async def get_from_table_by(
        self, model: type[T], *where_clauses: ColumnElement[bool]
    ) -> T | None:
        query = select(model).where(*where_clauses)
        results = await self.db.execute(query)

        return results.scalar_one_or_none()
