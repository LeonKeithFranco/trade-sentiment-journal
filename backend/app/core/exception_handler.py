from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from app.database.exceptions import DatabaseError


def attach_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers on the FastAPI instance.

    Args:
        app: The FastAPI application to attach the handlers to.
    """

    @app.exception_handler(DatabaseError)
    async def catch_database_error(
        request: Request, exc: DatabaseError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            content={"details": "Database cannot be reached."},
        )

    @app.exception_handler(Exception)
    async def catch_all_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "details": "An internal server error occurred. Please try again later."
            },
        )
