from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class InvalidCredentialsError(AppException):
    """Raised when authentication fails due to incorrect credentials."""

    status_code = 401  # Unauthorized
    error_code = ErrorCode.INVALID_CREDENTIALS
    message = "Incorrect email or password."
