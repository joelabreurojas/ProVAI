from enum import Enum


class ErrorCode(Enum):
    """
    Defines unique, application-wide error codes.
    These are organized by feature module for clarity.
    """

    # Generic Errors (0-999)
    INTERNAL_SERVER_ERROR = 0

    # Auth Errors (1000-1999)
    USER_ALREADY_EXISTS = 1001
    INVALID_CREDENTIALS = 1002
