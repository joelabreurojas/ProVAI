from src.application.errors import ErrorCode


class ApplicationException(Exception):
    """Base class for all application-specific exceptions."""

    status_code: int = 500  # Generic
    error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred"

    def __init__(
        self, message: str | None = None, status_code: int | None = None
    ) -> None:
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code

        super().__init__(self.message)


class UserAlreadyExistsError(Exception):
    """Raised when a user with the given email already exists."""

    status_code = 409  # Conflict
    error_code = ErrorCode.USER_ALREADY_EXISTS
    message = "A user with this email address already exists."


class InvalidCredentialsError(Exception):
    """Raised when authentication fails."""

    status_code = 401  # Unauthorized
    error_code = ErrorCode.INVALID_CREDENTIALS
    message = "Incorrect email or password."
