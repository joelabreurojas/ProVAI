from src.api.auth.application.exceptions.token_validation_error import (
    TokenValidationError,
)
from src.core.domain.errors import ErrorCode


class TokenExpiredError(TokenValidationError):
    """Raised when a JWT has expired."""

    error_code = ErrorCode.TOKEN_EXPIRED
    message = "Your session has expired. Please log in again."
