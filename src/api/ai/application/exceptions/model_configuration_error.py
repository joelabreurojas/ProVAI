from src.api.core.application.exceptions import AppException
from src.api.core.domain.errors import ErrorCode


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
