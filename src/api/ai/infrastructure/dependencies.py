from src.api.ai.infrastructure.model_cache import model_cache
from src.core.application.protocols import (
    EmbeddingServiceProtocol,
    LLMServiceProtocol,
)
from src.core.infrastructure.utils import provides


@provides(LLMServiceProtocol)
def get_llm_service() -> LLMServiceProtocol:
    """Provides the pre-loaded LLM service instance."""
    return model_cache.get_llm_service()


@provides(EmbeddingServiceProtocol)
def get_embedding_service() -> EmbeddingServiceProtocol:
    """Provides the pre-loaded Embedding service instance."""
    return model_cache.get_embedding_service()
