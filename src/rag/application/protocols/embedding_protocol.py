from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingServiceProtocol(Protocol):
    """
    Defines the contract for a service that can create text embeddings.
    """

    def embed_query(self, text: str) -> list[float]:
        """Creates an embedding for a single query string."""
        ...

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Creates embeddings for a batch of document strings."""
        ...
