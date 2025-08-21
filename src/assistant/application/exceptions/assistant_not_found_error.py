from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class AssistantNotFoundError(AppException):
    """Raised when an assistant is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.ASSISTANT_NOT_FOUND
    message = "The requested assistant was not found."

    def __init__(self, assistant_id: int):
        self.message = f"Assistant with id {assistant_id} not found."
        super().__init__(message=self.message)
