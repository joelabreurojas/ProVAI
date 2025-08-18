import logging
from functools import lru_cache

import psutil
from langchain_community.llms.llamacpp import LlamaCpp

from src.ai.application.exceptions import (
    ModelConfigurationError,
    ModelLoadError,
    ModelNotFoundError,
)
from src.ai.application.protocols import LLMServiceProtocol
from src.core.constants import PROJECT_ROOT
from src.core.dependencies import get_asset_manager_service

logger = logging.getLogger(__name__)


def _log_memory_usage() -> None:
    """Logs the current memory usage of the process."""
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"Current memory usage: {memory_info.rss / 1024**2:.2f} MB")


@lru_cache(maxsize=1)
def _load_llm_singleton() -> LlamaCpp:
    """
    Loads the Llama C++ model. This function is cached to ensure it runs only once.
    """
    logger.info("Starting to load the LLM...")
    _log_memory_usage()

    asset_manager = get_asset_manager_service()
    llm_config = asset_manager.get_llm_config()

    if not llm_config.filename:
        raise ModelConfigurationError(asset_type="LLM", field="filename")

    model_file_path = PROJECT_ROOT / "models" / llm_config.filename
    if not model_file_path.exists():
        raise ModelNotFoundError(model_path=model_file_path)

    try:
        llm = LlamaCpp(
            model_path=str(model_file_path),
            n_ctx=2048,
            n_gpu_layers=0,
            verbose=False,
            n_threads=4,
        )
    except Exception as e:
        logger.error(f"Failed to load LLM from path {model_file_path}: {e}")
        raise ModelLoadError() from e

    logger.info(f"LLM '{llm_config.name}' loaded successfully.")
    _log_memory_usage()
    return llm


class LLMService(LLMServiceProtocol):
    """
    Manages the lifecycle of the Large Language Model.
    """

    def get_llm(self) -> LlamaCpp:
        return _load_llm_singleton()
