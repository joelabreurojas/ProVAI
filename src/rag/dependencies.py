from fastapi import Depends
from langchain_chroma import Chroma
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session as SQLAlchemySession

from src.chat.application.protocols import ChatRepositoryProtocol
from src.chat.dependencies import get_chat_repository
from src.core.infrastructure.database import get_db
from src.rag.application.prompts import get_rag_prompt
from src.rag.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    DocumentServiceProtocol,
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.rag.application.services import DocumentService, IngestionService, RAGService
from src.rag.infrastructure.model_loader import get_embedding_model, get_llm
from src.rag.infrastructure.repositories import (
    SQLAlchemyChunkRepository,
    SQLAlchemyDocumentRepository,
)
from src.rag.infrastructure.vector_store import get_vector_store


# --- Protocol Implementations ---
def get_chunk_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> ChunkRepositoryProtocol:
    chunk_repo: ChunkRepositoryProtocol = SQLAlchemyChunkRepository(db)
    return chunk_repo


def get_document_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> DocumentRepositoryProtocol:
    doc_repo: DocumentRepositoryProtocol = SQLAlchemyDocumentRepository(db)
    return doc_repo


def get_rag_llm() -> LlamaCpp:
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


# --- Service Assemblers ---
def get_document_service(
    doc_repo: DocumentRepositoryProtocol = Depends(get_document_repository),
    chunk_repo: ChunkRepositoryProtocol = Depends(get_chunk_repository),
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
    vector_store: Chroma = Depends(get_rag_vector_store),
) -> DocumentServiceProtocol:
    return DocumentService(
        doc_repo=doc_repo,
        chunk_repo=chunk_repo,
        chat_repo=chat_repo,
        vector_store=vector_store,
    )


def get_ingestion_service(
    db: SQLAlchemySession = Depends(get_db),
    vector_store: Chroma = Depends(get_rag_vector_store),
    text_splitter: RecursiveCharacterTextSplitter = Depends(get_text_splitter),
    doc_repo: DocumentRepositoryProtocol = Depends(get_document_repository),
    chunk_repo: ChunkRepositoryProtocol = Depends(get_chunk_repository),
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
) -> IngestionServiceProtocol:
    return IngestionService(
        db=db,
        vector_store=vector_store,
        text_splitter=text_splitter,
        doc_repo=doc_repo,
        chunk_repo=chunk_repo,
        chat_repo=chat_repo,
    )


def get_rag_service(
    llm: LlamaCpp = Depends(get_rag_llm),
    vector_store: Chroma = Depends(get_rag_vector_store),
    prompt: ChatPromptTemplate = Depends(get_rag_prompt_template),
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
) -> RAGServiceProtocol:
    return RAGService(
        llm=llm, vector_store=vector_store, prompt=prompt, chat_repo=chat_repo
    )
