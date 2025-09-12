from src.api.ai.application.protocols import (
    EmbeddingServiceProtocol,
    LLMServiceProtocol,
)
from src.api.ai.application.services import EmbeddingService, LLMService


def get_llm_service() -> LLMServiceProtocol:
    """Provides a singleton instance of the LLMService."""
    return LLMService()


def get_embedding_service() -> EmbeddingServiceProtocol:
    """Provides a singleton instance of the EmbeddingService."""
    return EmbeddingService()
