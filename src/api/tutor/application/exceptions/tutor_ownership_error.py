from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class TutorOwnershipError(AppException):
    """
    Raised when a user attempts to modify a tutor they do not own.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.TUTOR_OWNERSHIP_REQUIRED
    message = "You are not the owner of this tutor."
