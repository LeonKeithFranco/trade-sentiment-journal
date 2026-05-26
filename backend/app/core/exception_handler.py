from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import (
    DatabaseError,
    InvalidAccessTokenError,
    TradeDoesNotExistError,
    UserAlreadyExistsError,
    UserInvalidCredentialsError,
)


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

    @app.exception_handler(UserInvalidCredentialsError)
    async def user_invalid_credentials_error_handler(
        request: Request, exc: UserInvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials."},
        )

    @app.exception_handler(InvalidAccessTokenError)
    async def invalid_access_token_error_handler(
        request: Request, exc: InvalidAccessTokenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.reason},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(TradeDoesNotExistError)
    async def trade_does_not_exist_error(
        equest: Request, exc: TradeDoesNotExistError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Trade does not exist."},
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
