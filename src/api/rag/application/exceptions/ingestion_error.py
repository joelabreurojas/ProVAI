from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class IngestionError(AppException):
    """Base exception for ingestion-related failures."""

    status_code = 500  # Internal Server Error
    error_code = ErrorCode.INGESTION_FAILED
    message = "An unexpected error occurred during document ingestion."
