from typing import Protocol, runtime_checkable

from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.embeddings import Embeddings


@runtime_checkable
class EmbeddingServiceProtocol(Protocol):
    """Defines the contract for the Embedding Model service."""

    def get_embedding_model(self) -> Embeddings: ...


@runtime_checkable
class LLMServiceProtocol(Protocol):
    """Defines the contract for the Language Model service."""

    def get_llm(self) -> LlamaCpp: ...
