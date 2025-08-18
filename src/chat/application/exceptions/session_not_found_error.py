from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class SessionNotFoundError(AppException):
    """Raised when a session is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.SESSION_NOT_FOUND
    message = "The requested session was not found."

    def __init__(self, session_id: int):
        self.message = f"Session {session_id} not found."
        super().__init__(message=self.message)
