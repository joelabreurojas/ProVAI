from src.auth.application.exceptions.token_validation_error import TokenValidationError
from src.core.domain.errors import ErrorCode


class TokenInvalidScopeError(TokenValidationError):
    """Raised when a JWT has an invalid or missing 'scope' claim."""

    error_code = ErrorCode.TOKEN_INVALID_SCOPE
    message = "The provided token is not valid for this action."
