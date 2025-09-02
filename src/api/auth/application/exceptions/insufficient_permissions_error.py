from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class InsufficientPermissionsError(AppException):
    """
    Raised when a user attempts an action that their global role
    (e.g., 'student') does not permit.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.INSUFFICIENT_PERMISSIONS
    message = "You do not have the required role to perform this action."
