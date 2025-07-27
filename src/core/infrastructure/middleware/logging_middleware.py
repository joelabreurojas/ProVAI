import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response

# Get the logger for this module
logger = logging.getLogger(__name__)


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Middleware to log incoming requests, their processing time, and response status.
    """
    start_time = time.time()

    # Process the request
    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000  # in milliseconds

    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time_ms": f"{process_time:.2f}",
    }

    # Log the information using the `extra` parameter to pass structured data
    logger.info("Request processed", extra={"extra_data": log_data})

    return response
