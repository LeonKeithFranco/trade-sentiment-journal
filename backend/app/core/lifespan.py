from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.model import get_model
from app.database import check_db_connection, dispose_engine


async def _start_up() -> None:
    await check_db_connection()
    get_model()


async def _tear_down() -> None:
    await dispose_engine()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.title = get_settings().app.name

    await _start_up()

    yield

    await _tear_down()
