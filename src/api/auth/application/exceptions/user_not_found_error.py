from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class UserNotFoundError(AppException):
    """Raised when a user with a given ID or email is not found."""

    status_code = 404  # Not Found
    error_code = ErrorCode.USER_NOT_FOUND
    message = "The requested user was not found."
