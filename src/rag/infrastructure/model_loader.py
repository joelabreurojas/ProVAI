import logging
from functools import lru_cache

import psutil
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_huggingface import HuggingFaceEmbeddings

from src.core.constants import PROJECT_ROOT
from src.core.dependencies import get_asset_manager_service
from src.rag.application.exceptions import (
    ModelConfigurationError,
    ModelLoadError,
    ModelNotFoundError,
)

logger = logging.getLogger(__name__)


def _log_memory_usage() -> None:
    """Logs the current memory usage of the process."""
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"Current memory usage: {memory_info.rss / 1024**2:.2f} MB")


@lru_cache(maxsize=1)
def get_llm() -> LlamaCpp:
    """
    Loads the Llama C++ model and wraps it in a LangChain-compliant class.
    Uses lru_cache to ensure the model is loaded only once (singleton).
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
            n_ctx=2048,  # The maximum context size
            n_gpu_layers=0,  # Explicitly run on CPU
            verbose=False,
            max_tokens=1024,
            temperature=0.7,
        )
    except Exception as e:
        raise ModelLoadError() from e

    logger.info(f"LLM '{llm_config.name}' loaded successfully.")
    _log_memory_usage()
    return llm


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Loads and returns the sentence-transformer embedding model.
    Uses lru_cache to ensure the model is loaded only once (singleton).
    """
    logger.info("Starting to load the embedding model...")
    _log_memory_usage()

    asset_manager = get_asset_manager_service()
    embed_config = asset_manager.get_embedding_model_config()

    if not embed_config.name:
        raise ModelConfigurationError(asset_type="Embedding Model", field="name")

    embedding_model = HuggingFaceEmbeddings(
        model_name=embed_config.name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    logger.info(f"Embedding model '{embed_config.name}' loaded successfully.")
    _log_memory_usage()
    return embedding_model
