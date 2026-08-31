import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime

import pytest
from app.core.app_factory import create_app
from app.database import Base
from app.database.session import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def pg_container() -> Iterator[PostgresContainer]:
    """Start a session-scoped PostgreSQL test container.

    Yields:
        PostgresContainer: The running Postgres container.
    """
    with PostgresContainer("docker.io/library/postgres:18-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def db_engine(pg_container: PostgresContainer) -> Iterator[Engine]:
    """Create a synchronous engine against the test container and set up the schema.

    Args:
        pg_container: The running Postgres test container.

    Yields:
        Engine: A synchronous SQLAlchemy engine with all tables created.
    """
    sync_url = pg_container.get_connection_url()
    sync_engine = create_engine(sync_url)

    Base.metadata.create_all(sync_engine)

    yield sync_engine

    sync_engine.dispose()


@pytest.fixture(autouse=True)
def clean_db(db_engine: Engine) -> None:
    """Truncate all tables in the test database before each test.

    Runs automatically before every test to ensure tests do not leak state
    between each other.

    Args:
        db_engine: The synchronous SQLAlchemy engine for the test database.
    """
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
    """Create an async session factory against the test container.

    Args:
        pg_container: The running Postgres test container.

    Yields:
        async_sessionmaker[AsyncSession]: A factory for creating async
            SQLAlchemy sessions against the test database.
    """
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
def app(mocker: MockerFixture) -> FastAPI:
    """Create a FastAPI application instance with the database connection check mocked.

    Args:
        mocker: The pytest-mock fixture used to patch check_db_connection.

    Returns:
        FastAPI: The configured application instance.
    """
    mocker.patch("app.core.lifespan.check_db_connection")

    return create_app()


@pytest.fixture
def client(
    app: FastAPI, async_session_factory: async_sessionmaker[AsyncSession]
) -> Iterator[TestClient]:
    """Create a TestClient with the database dependency overridden to use the test session.

    Args:
        app: The FastAPI application instance.
        async_session_factory: The async session factory for the test
            database.

    Yields:
        TestClient: A test client for making requests against the app.
    """

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def email() -> str:
    """Provide a default test user email address."""
    return "user@test.com"


@pytest.fixture
def access_token(client: TestClient, default_password: str, email: str) -> str:
    """Register and log in a test user, returning a valid access token.

    Args:
        client: The test client to make requests with.
        default_password: The password to register and log in with.
        email: The email address to register and log in with.

    Returns:
        str: A valid access token for the newly registered user.
    """
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
    """Register and log in a second test user, returning a valid access token.

    Used for tests that need to verify data isolation between users.

    Args:
        client: The test client to make requests with.
        default_password: The password to register and log in with.

    Returns:
        str: A valid access token for the newly registered second user.
    """
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
    """Provide a syntactically valid but unsigned/invalid JWT for negative auth tests."""
    return (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0."
        "KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
    )


@pytest.fixture
def trade_public_id(client: TestClient, access_token: str) -> str:
    """Create a trade for the authenticated test user, returning its public ID.

    Args:
        client: The test client to make requests with.
        access_token: A valid access token for the trade's owner.

    Returns:
        str: The public ID of the newly created trade.
    """
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
