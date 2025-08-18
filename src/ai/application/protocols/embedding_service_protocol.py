from typing import Protocol, runtime_checkable

from langchain_huggingface import HuggingFaceEmbeddings


@runtime_checkable
class EmbeddingServiceProtocol(Protocol):
    """Defines the contract for the Embedding Model service."""

    def get_embedding_model(self) -> HuggingFaceEmbeddings: ...
