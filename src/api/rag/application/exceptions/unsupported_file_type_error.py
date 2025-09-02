from src.api.core.domain.errors import ErrorCode
from src.api.rag.application.exceptions import IngestionError


class UnsupportedFileTypeError(IngestionError):
    """Raised when the user uploads a file that is not a PDF."""

    status_code = 415  # Unsupported Media Type
    error_code = ErrorCode.UNSUPPORTED_FILE_TYPE
    message = "Unsupported file type. Please upload a valid PDF document."
