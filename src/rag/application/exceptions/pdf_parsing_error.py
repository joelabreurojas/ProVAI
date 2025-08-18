from src.core.domain.errors import ErrorCode
from src.rag.application.exceptions import IngestionError


class PDFParsingError(IngestionError):
    """Raised when PyPDFLoader fails to parse a document."""

    status_code = 400  # Bad Request (the user's file is bad)
    error_code = ErrorCode.PDF_PARSING_FAILED
    message = "Failed to parse the provided PDF file. \
    It may be corrupt or improperly formatted."
