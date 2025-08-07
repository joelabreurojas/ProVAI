"""
This module serves as the Composition Root for the application.
It is the single place where all abstract protocols are wired to their
concrete implementations.
"""

from fastapi import Depends
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_cpp import Llama
from sqlalchemy.orm import Session

# Auth
from src.auth.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.auth.application.services import AuthService
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.auth.infrastructure.security import PasswordService, TokenService

# Core
from src.core.infrastructure.database import get_db
from src.rag.application.prompts import get_rag_prompt

# RAG
from src.rag.application.protocols.service_protocol import (
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.rag.application.services import IngestionService, RAGService
from src.rag.infrastructure.model_loader import get_embedding_model, get_llm
from src.rag.infrastructure.vector_store import get_vector_store

# Protocol Wiring


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryProtocol:
    return SQLAlchemyUserRepository(db)


def get_password_service() -> PasswordServiceProtocol:
    return PasswordService()


def get_token_service() -> TokenServiceProtocol:
    return TokenService()


def get_rag_llm() -> Llama:
    return get_llm()


def get_rag_embedding_model() -> HuggingFaceEmbeddings:
    return get_embedding_model()


def get_rag_vector_store(
    embedding_model: HuggingFaceEmbeddings = Depends(get_rag_embedding_model),
) -> Chroma:
    return get_vector_store(embedding_model)


def get_rag_prompt_template() -> ChatPromptTemplate:
    return get_rag_prompt()


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300, chunk_overlap=0, encoding_name="cl100k_base"
    )


# Service Assemblers


def get_auth_service(
    user_repo: UserRepositoryProtocol = Depends(get_user_repository),
    password_svc: PasswordServiceProtocol = Depends(get_password_service),
    token_svc: TokenServiceProtocol = Depends(get_token_service),
) -> AuthServiceProtocol:
    return AuthService(
        user_repo=user_repo, password_svc=password_svc, token_svc=token_svc
    )


def get_ingestion_service(
    vector_store: Chroma = Depends(get_rag_vector_store),
    text_splitter: RecursiveCharacterTextSplitter = Depends(get_text_splitter),
) -> IngestionServiceProtocol:
    return IngestionService(vector_store=vector_store, text_splitter=text_splitter)


def get_rag_service(
    llm: Llama = Depends(get_rag_llm),
    vector_store: Chroma = Depends(get_rag_vector_store),
    prompt: ChatPromptTemplate = Depends(get_rag_prompt_template),
) -> RAGServiceProtocol:
    return RAGService(llm=llm, vector_store=vector_store, prompt=prompt)
