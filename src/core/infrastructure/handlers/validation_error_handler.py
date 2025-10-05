from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handles Pydantic's RequestValidationError to provide a cleaner,
    more user-friendly error message, while being type-safe.
    """
    clean_msg = "Validation error"  # Default message

    if isinstance(exc, RequestValidationError):
        first_error = exc.errors()[0]

        raw_msg = first_error.get("msg", "Validation error")

        clean_msg = raw_msg.removeprefix("Value error, ")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": clean_msg}),
    )
