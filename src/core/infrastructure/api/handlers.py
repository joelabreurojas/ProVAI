from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import ApplicationException


async def application_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Global handler to catch and format all custom application exceptions.
    """

    # Handle custom application exceptions
    if isinstance(exc, ApplicationException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code.name,
                "message": exc.message,
            },
        )

    # Handle unexpected exceptions
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred.",
        },
    )
