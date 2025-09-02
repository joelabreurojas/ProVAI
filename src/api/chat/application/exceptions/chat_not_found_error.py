from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class ChatNotFoundError(AppException):
    """Raised when a chat is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.CHAT_NOT_FOUND
    message = "The requested chat was not found."

    def __init__(self, chat_id: int):
        self.message = f"Chat with id {chat_id} not found."
        super().__init__(message=self.message)
