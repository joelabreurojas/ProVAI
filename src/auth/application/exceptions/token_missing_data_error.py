from src.auth.application.exceptions.token_validation_error import TokenValidationError
from src.core.domain.errors import ErrorCode


class TokenMissingDataError(TokenValidationError):
    """Raised when a JWT is missing a required field (claim)."""

    error_code = ErrorCode.TOKEN_MISSING_DATA
    message = "The provided token is missing required data."

    def __init__(self, missing_claim: str | None = None):
        if missing_claim:
            self.message = f"Token is missing required claim: '{missing_claim}'."
        super().__init__(message=self.message)
