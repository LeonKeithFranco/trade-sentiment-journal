from fastapi import FastAPI
from sqlalchemy import text

from app.core.exception_handler import attach_exception_handlers
from app.core.lifespan import lifespan
from app.database import DbDependency
from app.database.exceptions import DatabaseError
from app.routes import routers


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.


    Attaches the applications exception handlers, registers all domain routers, and adds
    a health-check endpoint that verifies the database connectivity.

    Returns:
        FastAPI: The fully configured application instance.
    """
    app = FastAPI(lifespan=lifespan)

    attach_exception_handlers(app)

    for router in routers:
        app.include_router(router)

    @app.get("/health")
    async def health_check(db: DbDependency) -> dict[str, str]:
        try:
            await db.execute(text("SELECT 1"))
        except Exception as e:
            raise DatabaseError("Could not connect to database") from e

        return {"status": "ok"}

    return app
