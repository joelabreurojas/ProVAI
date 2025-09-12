import logging
from functools import lru_cache

from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings
from langsmith import traceable

from src.api.ai.application.exceptions import ModelConfigurationError, ModelLoadError
from src.api.ai.application.protocols import EmbeddingServiceProtocol
from src.core.application.utils.performance import log_memory_usage
from src.core.infrastructure.dependencies import get_asset_manager_service

logger = logging.getLogger(__name__)


class FastEmbedWrapper(Embeddings):
    def __init__(self, model_name: str):
        # This will download and cache the ONNX-optimized model on first run.
        self.model = TextEmbedding(model_name=model_name)

    @traceable(name="Embed Documents")
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # fastembed's embed method is designed for batching
        embeddings = self.model.embed(texts, batch_size=256, parallel=0)
        return [e.tolist() for e in embeddings]

    @traceable(name="Embed Query")
    def embed_query(self, text: str) -> list[float]:
        # For a single query, we just wrap it in a list.
        embedding = list(self.model.embed([text]))[0]
        embed_list: list[float] = embedding.tolist()
        return embed_list


@lru_cache(maxsize=1)
def _load_embedding_model_singleton() -> FastEmbedWrapper:
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
        embedding_model = FastEmbedWrapper(model_name=embed_config.name)
    except Exception as e:
        logger.error(f"Failed to load embedding model '{embed_config.name}': {e}")
        raise ModelLoadError() from e

    logger.info(f"Embedding model '{embed_config.name}' loaded successfully.")
    log_memory_usage(context="After Embedding Load")
    return embedding_model


class EmbeddingService(EmbeddingServiceProtocol):
    """
    Manages the lifecycle of the Embedding Model.
    """

    def get_embedding_model(self) -> Embeddings:
        return _load_embedding_model_singleton()
