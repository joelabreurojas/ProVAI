from src.core.domain.errors import ErrorCode

from .common_exceptions import AppException


class InvitationEmailMismatchError(AppException):
    """
    Raised when a user tries to accept an invitation that was created
    for a different email address.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.INVITATION_EMAIL_MISMATCH
    message = "This invitation is not valid for your account."


class InvitationNotFoundError(AppException):
    """
    Raised when an invitation token is not found in the database.
    """

    status_code = 404  # Not Found
    error_code = ErrorCode.INVITATION_NOT_FOUND
    message = "This invitation link is not valid or has been revoked by the teacher."


class SelfEnrollmentError(AppException):
    """Raised when a teacher attempts to enroll in their own tutor."""

    status_code = 400  # Bad Request
    error_code = ErrorCode.SELF_ENROLLMENT_NOT_ALLOWED
    message = "A teacher cannot enroll in their own assistant."


class UnenrollmentAuthorizationError(AppException):
    def __init__(self, message: str = "A user can only unenroll themselves."):
        super().__init__(
            status_code=403, error_code="UNENROLLMENT_NOT_AUTHORIZED", message=message
        )


class TutorNotFoundError(AppException):
    """Raised when a tutor is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.TUTOR_NOT_FOUND
    message = "The requested tutor was not found."

    def __init__(self, tutor_id: int):
        self.message = f"Tutor with id {tutor_id} not found."
        super().__init__(message=self.message)


class TutorOwnershipError(AppException):
    """
    Raised when a user attempts to modify a tutor they do not own.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.TUTOR_OWNERSHIP_REQUIRED
    message = "You are not the owner of this tutor."


class UserAlreadyEnrolledError(AppException):
    """Raised when a user is already enrolled in a tutor."""

    status_code = 409  # Conflict
    error_code = ErrorCode.USER_ALREADY_ENROLLED
    message = "This user is already enrolled in this tutor."


class UserNotEnrolledError(AppException):
    """
    Raised when a user attempts to interact with a tutor they are
    not enrolled in.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.USER_NOT_ENROLLED
    message = "You are not enrolled in this tutor's chat."
