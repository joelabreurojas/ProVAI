from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class InvalidPasswordError(AppException):
    """
    Raised when a user's password does not meet the required
    business logic for complexity.
    """

    status_code = 400  # Bad Request
    error_code = ErrorCode.INVALID_PASSWORD_FORMAT
    message = """
        Password must be at least 8 characters,
        include an uppercase letter, a number,
        and a special character.
    """
