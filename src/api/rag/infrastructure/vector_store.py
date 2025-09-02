from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from src.api.core.constants import PROJECT_ROOT


def get_vector_store(embedding_model: Embeddings) -> Chroma:
    """
    Initializes and returns a Chroma vector store instance.

    This function sets up a persistent, file-based vector store.
    """
    persist_dir_path = PROJECT_ROOT / "vector_store" / "provai.db"
    vector_store = Chroma(
        persist_directory=str(persist_dir_path),
        embedding_function=embedding_model,
    )
    return vector_store
