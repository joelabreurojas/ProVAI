from src.core.domain.errors import ErrorCode


class AppException(Exception):
    """Base class for all application-specific exceptions."""

    status_code: int = 500
    error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "An unexpected internal server error occurred."

    def __init__(
        self,
        message: str | None = None,
        status_code: int | None = None,
        error_code: ErrorCode | None = None,
    ):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        if error_code:
            self.error_code = error_code

        super().__init__(self.message)


class DatabaseError(AppException):
    """
    Raised when a database operation fails unexpectedly.
    This is a generic wrapper for lower-level SQLAlchemy exceptions.
    """

    status_code = 500  # Internal Server Error
    error_code = ErrorCode.DATABASE_ERROR
    message = "A database error occurred. Please try again later."
