from src.core.errors import ErrorCode
from src.core.exceptions import ApplicationException


class UserAlreadyExistsError(ApplicationException):
    """Raised when a user with the given email already exists."""

    status_code = 409  # Conflict
    error_code = ErrorCode.USER_ALREADY_EXISTS
    message = "A user with this email address already exists."


class InvalidCredentialsError(ApplicationException):
    """Raised when authentication fails due to incorrect credentials."""

    status_code = 401  # Unauthorized
    error_code = ErrorCode.INVALID_CREDENTIALS
    message = "Incorrect email or password."
