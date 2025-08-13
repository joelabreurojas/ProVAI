import numpy as np
from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings

from src.core.application.services.asset_service import AssetManagerService
from src.core.constants import PROJECT_ROOT
from src.rag.application.exceptions import ModelConfigurationError, ModelLoadError
from src.rag.application.protocols.embedding_protocol import EmbeddingServiceProtocol


class FastEmbedService(EmbeddingServiceProtocol, Embeddings):
    """
    A high-performance embedding service that conforms to both our
    internal protocol and LangChain's Embeddings interface.
    """

    def __init__(self, asset_manager: AssetManagerService):
        embed_config = asset_manager.get_embedding_model_config()

        if not embed_config.name:
            raise ModelConfigurationError(asset_type="Embedding Model", field="name")

        try:
            self._model = TextEmbedding(
                model_name=embed_config.name,
                cache_dir=str(PROJECT_ROOT / ".cache" / "fastembed_models"),
            )
        except Exception as e:
            raise ModelLoadError() from e

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Creates embeddings for a batch of documents."""
        # The model returns a generator of numpy arrays, so we convert them.
        embeddings: list[np.ndarray] = list(self._model.embed(texts))
        return [e.tolist() for e in embeddings]

    def embed_query(self, text: str) -> list[float]:
        """Creates an embedding for a single query."""
        # The model returns a generator, so we take the first and only result.
        embedding: np.ndarray = next(self._model.embed(text))
        return embedding.tolist()
