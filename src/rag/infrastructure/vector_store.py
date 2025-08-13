from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from src.core.constants import PROJECT_ROOT


def get_vector_store(embedding_function: Embeddings) -> Chroma:
    """
    Initializes and returns a Chroma vector store instance.

    This function sets up a persistent, file-based vector store.
    """
    vector_store = Chroma(
        persist_directory=str(PROJECT_ROOT / "vector_store"),
        embedding_function=embedding_function,
    )
    return vector_store
