from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.model import get_model
from app.database import check_db_connection, dispose_engine


async def _start_up() -> None:
    """Run application start up tasks.

    Raises:
        FileNotFoundError: If the sentiment model file does not exist.
    """
    await check_db_connection()
    get_model()


async def _tear_down() -> None:
    """Run application shutdown tasks."""
    await dispose_engine()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application start up and shutdown lifecycle.

    Args:
        app: The FastAPI application instance.

    Raises:
        FileNotFoundError: If the sentiment model file does not exist.
    """
    app.title = get_settings().app.name

    await _start_up()

    yield

    await _tear_down()
