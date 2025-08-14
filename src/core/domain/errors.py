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

    # RAG Errors (2000-2999)
    MODEL_NOT_FOUND = 2001
    MODEL_LOAD_FAILED = 2002
    MODEL_CONFIG_ERROR = 2003
