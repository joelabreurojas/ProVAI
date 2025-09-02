import json
import logging
from typing import Any


class JsonFormatter(logging.Formatter):
    """
    Formats log records into a JSON string.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_object: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
        }
        # Add extra fields from the log call, if any
        if hasattr(record, "extra_data"):
            log_object.update(record.extra_data)

        return json.dumps(log_object)


def setup_logging() -> None:
    """
    Configures the root logger for the application.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a handler to output to the console
    handler = logging.StreamHandler()

    # Set our custom JSON formatter on the handler
    formatter = JsonFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
