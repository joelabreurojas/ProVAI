import logging

from src.api.ai.application.services import EmbeddingService, LLMService
from src.core.application.protocols import (
    EmbeddingServiceProtocol,
    LLMServiceProtocol,
)

logger = logging.getLogger(__name__)


class ModelCache:
    """
    A singleton-like container to load and hold the AI models once during
    the application's lifespan.
    """

    _llm_service: LLMServiceProtocol | None = None
    _embedding_service: EmbeddingServiceProtocol | None = None

    @classmethod
    def load_models(cls) -> None:
        """
        Loads all AI models into memory. This should be called only once
        during the application startup event.
        """
        if cls._llm_service is None:
            cls._llm_service = LLMService()
        if cls._embedding_service is None:
            cls._embedding_service = EmbeddingService()

    @classmethod
    def get_llm_service(cls) -> LLMServiceProtocol:
        if cls._llm_service is None:
            raise RuntimeError("LLM Service has not been initialized.")
        return cls._llm_service

    @classmethod
    def get_embedding_service(cls) -> EmbeddingServiceProtocol:
        if cls._embedding_service is None:
            raise RuntimeError("Embedding Service has not been initialized.")
        return cls._embedding_service


# Create a single instance that the app will use
model_cache = ModelCache()
