from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class UserNotEnrolledError(AppException):
    """
    Raised when a user attempts to interact with a tutor they are
    not enrolled in.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.USER_NOT_ENROLLED
    message = "You are not enrolled in this tutor's chat."
