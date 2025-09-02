from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class InvitationEmailMismatchError(AppException):
    """
    Raised when a user tries to accept an invitation that was created
    for a different email address.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.INVITATION_EMAIL_MISMATCH
    message = "This invitation is not valid for your account."
