from langchain_community.vectorstores.chroma import Chroma
from langchain_core.embeddings import Embeddings


def get_vector_store(embedding_model: Embeddings) -> Chroma:
    """
    Initializes and returns a Chroma vector store instance.

    This function sets up a persistent, file-based vector store.
    """
    vector_store = Chroma(
        persist_directory="./vector_store/provai.db",
        embedding_function=embedding_model,
    )
    return vector_store
