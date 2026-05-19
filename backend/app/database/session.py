from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

engine = create_async_engine(
    str(get_settings().db.url),
    echo=get_settings().app.debug,
    pool_pre_ping=True,
)


AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session


DbDependency = Annotated[AsyncSession, Depends(get_db)]
