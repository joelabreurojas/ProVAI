from src.core.application.exceptions.app_exception import AppException
from src.core.domain.errors import ErrorCode


class DatabaseError(AppException):
    """
    Raised when a database operation fails unexpectedly.
    This is a generic wrapper for lower-level SQLAlchemy exceptions.
    """

    status_code = 500  # Internal Server Error
    error_code = ErrorCode.DATABASE_ERROR
    message = "A database error occurred. Please try again later."
