from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database.exceptions import DatabaseError
from app.domains.auth.exceptions import UserAlreadyExistsError


def attach_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers on the FastAPI instance.

    Args:
        app: The FastAPI application to attach the handlers to.
    """

    @app.exception_handler(DatabaseError)
    async def catch_database_error_handler(
        request: Request, exc: DatabaseError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Database cannot be reached."},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_error_handler(
        request: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "User already exists."},
        )

    @app.exception_handler(Exception)
    async def catch_all_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred. Please try again later."
            },
        )
