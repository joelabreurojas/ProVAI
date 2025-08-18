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

    # AI Model Errors (2000-2999)
    MODEL_NOT_FOUND = 2001
    MODEL_LOAD_FAILED = 2002
    MODEL_CONFIG_ERROR = 2003

    # RAG  Errors (3000-3999)
    DOCUMENT_NOT_FOUND = 3001
    INGESTION_FAILED = 3002
    PDF_PARSING_FAILED = 3003

    # Chat Errors (4000-4999)
    CHAT_NOT_FOUND = 4001
    SESSION_NOT_FOUND = 4002
    MESSAGE_CREATION_FAILED = 4003
