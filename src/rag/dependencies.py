from fastapi import Depends
from langchain_chroma import Chroma
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.chat.application.protocols import ContentRepositoryProtocol
from src.chat.dependencies import get_content_repository
from src.rag.application.prompts import get_rag_prompt
from src.rag.application.protocols import (
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.rag.application.services import IngestionService, RAGService
from src.rag.infrastructure.model_loader import get_embedding_model, get_llm
from src.rag.infrastructure.vector_store import get_vector_store


# --- Protocol Implementations for RAG ---
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


# --- Service Assemblers for RAG ---
def get_ingestion_service(
    vector_store: Chroma = Depends(get_rag_vector_store),
    text_splitter: RecursiveCharacterTextSplitter = Depends(get_text_splitter),
    content_repo: ContentRepositoryProtocol = Depends(get_content_repository),
) -> IngestionServiceProtocol:
    return IngestionService(
        vector_store=vector_store,
        text_splitter=text_splitter,
        content_repo=content_repo,
    )


def get_rag_service(
    llm: LlamaCpp = Depends(get_rag_llm),
    vector_store: Chroma = Depends(get_rag_vector_store),
    prompt: ChatPromptTemplate = Depends(get_rag_prompt_template),
) -> RAGServiceProtocol:
    return RAGService(llm=llm, vector_store=vector_store, prompt=prompt)
