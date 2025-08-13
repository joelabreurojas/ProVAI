from langchain_chroma import Chroma
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.dependencies import get_asset_manager_service
from src.rag.application.prompts import get_rag_prompt
from src.rag.application.protocols import (
    EmbeddingServiceProtocol,
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.rag.application.services import IngestionService, RAGService
from src.rag.infrastructure.embedding import FastEmbedService
from src.rag.infrastructure.model_loader import get_llm
from src.rag.infrastructure.vector_store import get_vector_store

# --- Builder Functions (No FastAPI) ---


def build_rag_llm() -> LlamaCpp:
    """Builds and returns the LLM."""
    return get_llm()


def build_embedding_service() -> EmbeddingServiceProtocol:
    """Builds and returns the MVP embedding service (FastEmbedService)."""
    asset_manager = get_asset_manager_service()
    return FastEmbedService(asset_manager)


def build_rag_vector_store(
    embedding_service: EmbeddingServiceProtocol,
) -> Chroma:
    """Builds and returns the vector store, requiring an embedding service."""
    return get_vector_store(embedding_function=embedding_service)


def build_rag_prompt_template() -> ChatPromptTemplate:
    """Builds and returns the MVP prompt template (context-grounded, simple)."""
    return get_rag_prompt()


def build_text_splitter() -> RecursiveCharacterTextSplitter:
    """Builds and returns the MVP chunk splitter (1000 chars, no overlap)."""
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0, encoding_name="cl100k_base"
    )


# --- Service Builders ---


def build_ingestion_service() -> IngestionServiceProtocol:
    """Constructs the IngestionService with all its real dependencies."""
    embedding_service = build_embedding_service()
    vector_store = build_rag_vector_store(embedding_service)
    text_splitter = build_text_splitter()
    return IngestionService(vector_store=vector_store, text_splitter=text_splitter)


def build_rag_service() -> RAGServiceProtocol:
    """Constructs the RAGService with all its real dependencies."""
    llm = build_rag_llm()
    embedding_service = build_embedding_service()
    vector_store = build_rag_vector_store(embedding_service)
    prompt = build_rag_prompt_template()
    return RAGService(llm=llm, vector_store=vector_store, prompt=prompt)


# --- FastAPI Dependency Providers ---


def get_ingestion_service() -> IngestionServiceProtocol:
    """FastAPI dependency provider for the IngestionService."""
    return build_ingestion_service()


def get_rag_service() -> RAGServiceProtocol:
    """FastAPI dependency provider for the RAGService."""
    return build_rag_service()
