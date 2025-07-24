from enum import Enum


class ErrorCode(Enum):
    """Defines unique, application-wide error codes."""

    # --- Authentiication Errors (1000-1999) ---
    USER_ALREADY_EXISTS = 1000
    INVALID_CREDENTIALS = 1001
