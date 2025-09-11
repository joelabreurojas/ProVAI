from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class UserAlreadyEnrolledError(AppException):
    """Raised when a user is already enrolled in a tutor."""

    status_code = 409  # Conflict
    error_code = ErrorCode.USER_ALREADY_ENROLLED
    message = "This user is already enrolled in this tutor."
