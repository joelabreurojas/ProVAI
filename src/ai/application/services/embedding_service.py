import logging
from functools import lru_cache

import psutil
from langchain_huggingface import HuggingFaceEmbeddings

from src.core.application.utils.performance import log_memory_usage
from src.ai.application.exceptions import ModelConfigurationError, ModelLoadError
from src.ai.application.protocols import EmbeddingServiceProtocol
from src.core.dependencies import get_asset_manager_service

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_embedding_model_singleton() -> HuggingFaceEmbeddings:
    """
    Loads the embedding model. This function is cached to ensure it runs only once.
    """
    logger.info("Starting to load the embedding model...")
    log_memory_usage(context="Before Embedding Load")

    asset_manager = get_asset_manager_service()
    embed_config = asset_manager.get_embedding_model_config()

    if not embed_config.name:
        raise ModelConfigurationError(asset_type="Embedding", field="name")

    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name=embed_config.name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    except Exception as e:
        logger.error(
            f"Failed to load embedding model '{embed_config.name}' \
            from HuggingFace: {e}"
        )
        raise ModelLoadError() from e

    logger.info(f"Embedding model '{embed_config.name}' loaded successfully.")
    log_memory_usage(context="After Embedding Load")
    return embedding_model


class EmbeddingService(EmbeddingServiceProtocol):
    """
    Manages the lifecycle of the Embedding Model.
    """

    def get_embedding_model(self) -> HuggingFaceEmbeddings:
        return _load_embedding_model_singleton()
