import logging

import psutil

logger = logging.getLogger(__name__)


def log_memory_usage(context: str = "Default") -> None:
    """Logs the current memory usage of the process with context."""
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"[{context}] Current memory usage: {memory_info.rss / 1024**2:.2f} MB")
