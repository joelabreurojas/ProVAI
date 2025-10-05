from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles Pydantic's RequestValidationError to provide a cleaner,
    more user-friendly error message.
    """
    # Get the first error from the list
    first_error = exc.errors()[0]

    raw_msg = first_error.get("msg", "Validation error")

    # Clean up the "Value error, " prefix
    clean_msg = raw_msg.removeprefix("Value error, ")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": clean_msg}),
    )
