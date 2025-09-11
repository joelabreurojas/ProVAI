from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class InsufficientPermissionsError(AppException):
    """
    Raised when a user attempts an action that their global role
    (e.g., 'student') does not permit.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.INSUFFICIENT_PERMISSIONS
    message = "You do not have the required role to perform this action."
