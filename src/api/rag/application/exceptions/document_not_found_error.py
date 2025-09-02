from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class DocumentNotFoundError(AppException):
    """Raised when a document is not found in the database."""

    status_code = 404  # Not Found
    error_code = ErrorCode.DOCUMENT_NOT_FOUND
    message = "The requested document was not found."

    def __init__(self, document_id: int):
        self.message = f"Document {document_id} not found."
        super().__init__(message=self.message)
