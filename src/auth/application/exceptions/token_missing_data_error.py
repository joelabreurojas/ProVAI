from src.auth.application.exceptions.token_validation_error import TokenValidationError
from src.core.domain.errors import ErrorCode


class TokenMissingDataError(TokenValidationError):
    """Raised when a JWT is missing a required field."""

    error_code = ErrorCode.TOKEN_MISSING_DATA
    message = "The provided token is missing required data."
