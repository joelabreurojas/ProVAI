from src.api.ai.application.services import EmbeddingService, LLMService
from src.core.application.protocols import (
    EmbeddingServiceProtocol,
    LLMServiceProtocol,
)
from src.core.infrastructure.utils import provides


@provides(LLMServiceProtocol)
def get_llm_service() -> LLMServiceProtocol:
    """Provides a singleton instance of the LLMService."""
    return LLMService()


@provides(EmbeddingServiceProtocol)
def get_embedding_service() -> EmbeddingServiceProtocol:
    """Provides a singleton instance of the EmbeddingService."""
    return EmbeddingService()
