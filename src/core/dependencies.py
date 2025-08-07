"""
This module serves as the Composition Root for the application.

It is the single place where all abstract protocols are wired to their
concrete implementations from the infrastructure layer. FastAPI's `Depends`
will use the provider functions defined here to inject dependencies into
the API endpoints and other services.
"""

from fastapi import Depends
from langchain_community.vectorstores.chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama
from sqlalchemy.orm import Session

# --- Auth Protocols ---
from src.auth.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)

# --- Auth Concrete Implementations ---
from src.auth.application.services.auth_service import AuthService
from src.auth.infrastructure.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.security.password_service import PasswordService
from src.auth.infrastructure.security.token_service import TokenService

# --- Core Dependencies ---
from src.core.infrastructure.database import get_db
from src.rag.application.services.ingestion_service import IngestionService

# --- RAG Concrete Implementations ---
from src.rag.infrastructure.model_loader import get_embedding_model, get_llm
from src.rag.infrastructure.vector_store import get_vector_store

# --- Protocol Implementations (The "Wiring") ---


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryProtocol:
    """Provides a concrete SQLAlchemy implementation of the UserRepositoryProtocol."""
    return SQLAlchemyUserRepository(db)


def get_password_service() -> PasswordServiceProtocol:
    """Provides a concrete implementation of the PasswordServiceProtocol."""
    return PasswordService()


def get_token_service() -> TokenServiceProtocol:
    """Provides a concrete implementation of the TokenServiceProtocol."""
    return TokenService()


# --- Service Dependencies (The "Assembler") ---


def get_auth_service(
    user_repo: UserRepositoryProtocol = Depends(get_user_repository),
    password_svc: PasswordServiceProtocol = Depends(get_password_service),
    token_svc: TokenServiceProtocol = Depends(get_token_service),
) -> AuthServiceProtocol:
    """
    Constructs and provides the main AuthService, assembling it with all
    its concrete dependencies.
    """
    return AuthService(
        user_repo=user_repo,
        password_svc=password_svc,
        token_svc=token_svc,
    )


# --- RAG Model Providers ---


def get_rag_llm() -> Llama:
    """Provides the singleton instance of the LLM."""
    return get_llm()


def get_rag_embedding_model() -> HuggingFaceEmbeddings:
    """Provides the singleton instance of the embedding model."""
    return get_embedding_model()


def get_rag_vector_store(
    embedding_model: HuggingFaceEmbeddings = Depends(get_rag_embedding_model),
) -> Chroma:
    """Provides the singleton instance of the Chroma vector store."""
    return get_vector_store(embedding_model)


def get_ingestion_service(
    vector_store: Chroma = Depends(get_rag_vector_store),
) -> IngestionService:  # This should be a Protocol
    """Constructs and provides the main IngestionService."""
    return IngestionService(vector_store)