from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode


class ModelLoadError(AppException):
    """
    Raised when a model file is found but fails to load for other reasons,
    such as being corrupted or incompatible.
    """

    status_code = 500
    error_code = ErrorCode.MODEL_LOAD_FAILED
    message = "An unexpected error occurred while loading the AI model."
