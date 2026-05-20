from sqlalchemy.ext.asyncio import AsyncSession


class Repository:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def commit(self) -> None:
        await self.db.commit()
