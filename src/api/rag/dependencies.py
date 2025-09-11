from fastapi import Depends
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.ai.application.protocols import (
    EmbeddingServiceProtocol,
    LLMServiceProtocol,
)
from src.api.ai.dependencies import get_embedding_service, get_llm_service
from src.api.rag.application.prompts import get_rag_prompt
from src.api.rag.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    DocumentServiceProtocol,
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.api.rag.application.services import (
    DocumentService,
    IngestionService,
    RAGService,
)
from src.api.rag.infrastructure.repositories import (
    SQLAlchemyChunkRepository,
    SQLAlchemyDocumentRepository,
)
from src.api.rag.infrastructure.vector_store import get_vector_store
from src.api.tutor.application.protocols import TutorRepositoryProtocol
from src.api.tutor.dependencies import get_tutor_repository
from src.core.infrastructure.database import get_db


# --- Protocol Implementations ---
def get_chunk_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> ChunkRepositoryProtocol:
    return SQLAlchemyChunkRepository(db)


def get_document_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> DocumentRepositoryProtocol:
    return SQLAlchemyDocumentRepository(db)


def get_rag_vector_store(
    embedding_service: EmbeddingServiceProtocol = Depends(get_embedding_service),
) -> Chroma:
    embedding_model = embedding_service.get_embedding_model()
    return get_vector_store(embedding_model)


def get_rag_prompt_template() -> ChatPromptTemplate:
    return get_rag_prompt()


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300, chunk_overlap=0, encoding_name="cl100k_base"
    )


def get_document_service(
    doc_repo: DocumentRepositoryProtocol = Depends(get_document_repository),
    chunk_repo: ChunkRepositoryProtocol = Depends(get_chunk_repository),
    tutor_repo: TutorRepositoryProtocol = Depends(get_tutor_repository),
    vector_store: Chroma = Depends(get_rag_vector_store),
) -> DocumentServiceProtocol:
    return DocumentService(
        doc_repo=doc_repo,
        chunk_repo=chunk_repo,
        tutor_repo=tutor_repo,
        vector_store=vector_store,
    )


# --- Service Assemblers ---
def get_ingestion_service(
    db: SQLAlchemySession = Depends(get_db),
    vector_store: Chroma = Depends(get_rag_vector_store),
    text_splitter: RecursiveCharacterTextSplitter = Depends(get_text_splitter),
    doc_repo: DocumentRepositoryProtocol = Depends(get_document_repository),
    chunk_repo: ChunkRepositoryProtocol = Depends(get_chunk_repository),
) -> IngestionServiceProtocol:
    return IngestionService(
        db=db,
        vector_store=vector_store,
        text_splitter=text_splitter,
        doc_repo=doc_repo,
        chunk_repo=chunk_repo,
    )


def get_rag_service(
    llm_service: LLMServiceProtocol = Depends(get_llm_service),
    vector_store: Chroma = Depends(get_rag_vector_store),
    prompt: ChatPromptTemplate = Depends(get_rag_prompt_template),
) -> RAGServiceProtocol:
    llm = llm_service.get_llm()
    return RAGService(
        llm=llm,
        vector_store=vector_store,
        prompt=prompt,
    )
