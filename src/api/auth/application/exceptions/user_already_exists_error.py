from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class UserAlreadyExistsError(AppException):
    """Raised when a user with the given email already exists."""

    status_code = 409  # Conflict
    error_code = ErrorCode.USER_ALREADY_EXISTS
    message = "A user with this email address already exists."
