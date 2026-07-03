from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.database.exceptions import DatabaseError

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


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield an async SQLAlchemy session for the duration of a request.

    Used as a FastAPI dependency. The session is automatically closed when the request
    completes.

    Yields:
        AsyncSession: A scoped async database session.
    """
    async with AsyncSessionFactory() as session:
        yield session


DbDependency = Annotated[AsyncSession, Depends(get_db)]


async def check_db_connection() -> None:
    """Verify that the database is reachable.

    Raises:
        DatabaseError: If the database cannot be reached or the query fails.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        raise DatabaseError("Could not connect to database") from e


async def dispose_engine() -> None:
    """Dispose of the database engine, closing all pooled connections."""
    await engine.dispose()
