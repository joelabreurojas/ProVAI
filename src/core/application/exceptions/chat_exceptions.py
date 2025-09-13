from src.core.domain.errors import ErrorCode

from .common_exceptions import AppException


class ChatNotFoundError(AppException):
    """Raised when a chat is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.CHAT_NOT_FOUND
    message = "The requested chat was not found."

    def __init__(self, chat_id: int):
        self.message = f"Chat with id {chat_id} not found."
        super().__init__(message=self.message)


class ChatOwnershipError(AppException):
    """Raised when a user attempts to access a chat they do not own."""

    status_code = 403  # Forbidden
    error_code = ErrorCode.CHAT_OWNERSHIP_REQUIRED
    message = "You are not the owner of this chat."


class MessageCreationError(AppException):
    """Raised when a message fails to be created."""

    status_code = 500  # Internal Server Error
    error_code = ErrorCode.MESSAGE_CREATION_FAILED
    message = "Could not save the message to the chat."
