from src.core.domain.errors import ErrorCode

from .common_exceptions import AppException


class DocumentNotFoundError(AppException):
    """Raised when a document is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.DOCUMENT_NOT_FOUND
    message = "The requested document was not found."

    def __init__(self, document_id: int):
        self.message = f"Document {document_id} not found."
        super().__init__(message=self.message)


class IngestionError(AppException):
    """Base exception for ingestion-related failures."""

    status_code = 500  # Internal Server Error
    error_code = ErrorCode.INGESTION_FAILED
    message = "An unexpected error occurred during document ingestion."


class PDFParsingError(IngestionError):
    """Raised when PyPDFLoader fails to parse a document."""

    status_code = 400  # Bad Request (the user's file is bad)
    error_code = ErrorCode.PDF_PARSING_FAILED
    message = "Failed to parse the provided PDF file. \
    It may be corrupt or improperly formatted."


class UnsupportedFileTypeError(IngestionError):
    """Raised when the user uploads a file that is not a PDF."""

    status_code = 415  # Unsupported Media Type
    error_code = ErrorCode.UNSUPPORTED_FILE_TYPE
    message = "Unsupported file type. Please upload a valid PDF document."
