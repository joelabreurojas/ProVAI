from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class TutorNotFoundError(AppException):
    """Raised when a tutor is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.TUTOR_NOT_FOUND
    message = "The requested tutor was not found."

    def __init__(self, tutor_id: int):
        self.message = f"Tutor with id {tutor_id} not found."
        super().__init__(message=self.message)
