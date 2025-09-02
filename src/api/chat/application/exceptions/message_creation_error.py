from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class MessageCreationError(AppException):
    """Raised when a message fails to be created."""

    status_code = 500  # Internal Server Error
    error_code = ErrorCode.MESSAGE_CREATION_FAILED
    message = "Could not save the message to the chat."
