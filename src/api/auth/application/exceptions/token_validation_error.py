from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class TokenValidationError(AppException):
    """Base class for all JWT validation errors. Defaults to 401."""

    status_code = 401
    error_code = ErrorCode.TOKEN_VALIDATION_ERROR
    message = "Could not validate credentials. Please log in again."
