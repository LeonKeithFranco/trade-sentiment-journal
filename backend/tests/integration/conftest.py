import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime

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
    with PostgresContainer("docker.io/library/postgres:18-alpine") as container:
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
) -> Iterator[async_sessionmaker[AsyncSession]]:
    async_url = pg_container.get_connection_url().replace("psycopg2", "asyncpg")

    async_engine = create_async_engine(async_url)

    yield async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    asyncio.run(async_engine.dispose())


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


@pytest.fixture
def access_token(client: TestClient, default_password: str) -> str:
    email = "user@test.com"

    client.post("/auth/register", json={"email": email, "password": default_password})

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": default_password,
        },
    )

    return login_response.json()["access_token"]


@pytest.fixture
def other_access_token(client: TestClient, default_password: str) -> str:
    email = "user2@test.com"

    client.post("/auth/register", json={"email": email, "password": default_password})

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": default_password,
        },
    )

    return login_response.json()["access_token"]


@pytest.fixture(scope="session")
def fake_access_token() -> str:
    return (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0."
        "KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
    )


@pytest.fixture
def trade_public_id(client: TestClient, access_token: str) -> str:
    payload = {
        "ticker": "MAPPL",
        "direction": "LONG",
        "position_size": 3.33,
        "entry_price": 50.51,
        "exit_price": None,
        "opened_at": datetime.now(UTC).isoformat(),
        "closed_at": None,
    }

    response = client.post(
        "/trades",
        headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    return response.json()["public_id"]
