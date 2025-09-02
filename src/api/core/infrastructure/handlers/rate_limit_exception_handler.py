from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


def rate_limit_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global handler for SlowAPI's RateLimitExceeded exception.
    """
    detail = "Rate limit exceeded"
    if isinstance(exc, RateLimitExceeded):
        detail = exc.detail

    return JSONResponse(
        status_code=429,
        content={
            "error_code": "RATE_LIMIT_EXCEEDED",
            "message": f"Rate limit exceeded: {detail}",
        },
    )
