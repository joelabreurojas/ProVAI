from src.core.domain.errors import ErrorCode

from .common_exceptions import AppException


class InsufficientPermissionsError(AppException):
    """
    Raised when a user attempts an action that their global role
    (e.g., 'student') does not permit.
    """

    status_code = 403  # Forbidden
    error_code = ErrorCode.INSUFFICIENT_PERMISSIONS
    message = "You do not have the required role to perform this action."


class InvalidCredentialsError(AppException):
    """Raised when authentication fails due to incorrect credentials."""

    status_code = 401  # Unauthorized
    error_code = ErrorCode.INVALID_CREDENTIALS
    message = "Incorrect email or password."


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


class TokenValidationError(AppException):
    """Base class for all JWT validation errors. Defaults to 401."""

    status_code = 401
    error_code = ErrorCode.TOKEN_VALIDATION_ERROR
    message = "Could not validate credentials. Please log in again."


class TokenExpiredError(TokenValidationError):
    """Raised when a JWT has expired."""

    error_code = ErrorCode.TOKEN_EXPIRED
    message = "Your session has expired. Please log in again."


class TokenInvalidScopeError(TokenValidationError):
    """Raised when a JWT has an invalid or missing 'scope' claim."""

    error_code = ErrorCode.TOKEN_INVALID_SCOPE
    message = "The provided token is not valid for this action."


class TokenMissingDataError(TokenValidationError):
    """Raised when a JWT is missing a required field (claim)."""

    error_code = ErrorCode.TOKEN_MISSING_DATA
    message = "The provided token is missing required data."

    def __init__(self, missing_claim: str | None = None):
        if missing_claim:
            self.message = f"Token is missing required claim: '{missing_claim}'."
        super().__init__(message=self.message)


class UserAlreadyExistsError(AppException):
    """Raised when a user with the given email already exists."""

    status_code = 409  # Conflict
    error_code = ErrorCode.USER_ALREADY_EXISTS
    message = "A user with this email address already exists."


class UserNotFoundError(AppException):
    """Raised when a user with a given ID or email is not found."""

    status_code = 404  # Not Found
    error_code = ErrorCode.USER_NOT_FOUND
    message = "The requested user was not found."
