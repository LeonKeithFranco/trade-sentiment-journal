from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


def attach_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers on the FastAPI instance.

    Args:
        app: The FastAPI application to attach the handlers to.
    """

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
