from collections.abc import AsyncIterator, Iterator

import pytest
from app.core.app_factory import create_app
from app.database import Base
from app.database.session import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def pg_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("docker.io/library/postgres:18-alphine") as container:
        yield container


@pytest.fixture(scope="session")
def db_engine(pg_container: PostgresContainer) -> Iterator[Engine]:
    sync_url = pg_container.get_connection_url()
    sync_engine = create_engine(sync_url)

    Base.metadata.create_all(sync_engine)

    yield sync_engine

    sync_engine.dispose()


@pytest.fixture(autouse=True)
def clean_db(db_engine: Engine) -> None:
    with db_engine.connect() as conn:
        result = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = result.scalars().all()

        if not tables:
            return

        table_list = ", ".join(f'"{table}"' for table in tables)
        conn.execute(text(f"TRUNCATE {table_list} RESTART IDENTITY CASCADE"))
        conn.commit()


@pytest.fixture
def async_session_factory(
    pg_container: PostgresContainer,
) -> async_sessionmaker[AsyncSession]:
    async_url = pg_container.get_connection_url().replace("psycopg2", "asyncpg")

    async_engine = create_async_engine(async_url)

    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(
    app: FastAPI, async_session_factory: async_sessionmaker[AsyncSession]
) -> Iterator[TestClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
