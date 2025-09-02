from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class SelfEnrollmentError(AppException):
    """Raised when a teacher attempts to enroll in their own tutor."""

    status_code = 400  # Bad Request
    error_code = ErrorCode.SELF_ENROLLMENT_NOT_ALLOWED
    message = "A teacher cannot enroll as a student in their own tutor."
