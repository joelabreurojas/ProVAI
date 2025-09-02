from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class InvitationNotFoundError(AppException):
    """
    Raised when an invitation token is not found in the database.
    """

    status_code = 404  # Not Found
    error_code = ErrorCode.INVITATION_NOT_FOUND
    message = "This invitation link is not valid or has been revoked by the teacher."
