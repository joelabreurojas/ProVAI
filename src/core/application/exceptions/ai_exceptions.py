from pathlib import Path

from src.core.domain.errors import ErrorCode

from .common_exceptions import AppException


class ModelConfigurationError(AppException):
    """
    Raised when a model's configuration in the asset registry is
    incomplete or invalid (e.g., missing a required filename).
    """

    status_code = 500
    error_code = ErrorCode.MODEL_CONFIG_ERROR
    message = "A required AI model asset is configured incorrectly."

    def __init__(self, asset_type: str, field: str):
        self.message = (
            f"Invalid configuration for {asset_type}: "
            f"The required '{field}' is missing or empty in the asset registry."
        )
        super().__init__(message=self.message)


class ModelLoadError(AppException):
    """
    Raised when a model file is found but fails to load for other reasons,
    such as being corrupted or incompatible.
    """

    status_code = 500
    error_code = ErrorCode.MODEL_LOAD_FAILED
    message = "An unexpected error occurred while loading the AI model."


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
