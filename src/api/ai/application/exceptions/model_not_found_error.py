from pathlib import Path

from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


class ModelNotFoundError(AppException):
    """
    Raised when a required AI model file is not found on the filesystem.
    This typically indicates a setup or configuration error.
    """

    status_code = 500
    error_code = ErrorCode.MODEL_NOT_FOUND
    message = "Model file not found at the configured path."

    # Pass the model path to the constructor
    def __init__(self, model_path: Path):
        self.message = (
            f"Model file not found at the configured path: '{model_path}'. "
            "Please ensure the model has been downloaded by running the "
            "`scripts/download_assets.sh` script."
        )
        super().__init__(message=self.message)
