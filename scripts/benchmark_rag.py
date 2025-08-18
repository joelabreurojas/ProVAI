"""
A simple script to measure the performance of the RAG pipeline.

This script seeds the database with necessary records, runs a warm-up query to
load AI models into memory, then benchmarks the ingestion and query processes.

Example:
python -m scripts.benchmark_rag --doc-path "sample_data/scipy-lectures.pdf" \
--query "What is the main difference between a NumPy array and a standard Python list?"
"""

import argparse
import logging
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv

from src.auth.domain.models import User
from src.chat.domain.models import Chat
from src.chat.infrastructure.repositories import SQLAlchemyChatRepository
from src.core.infrastructure.database import SessionLocal
from src.core.modules import import_models
from src.rag.application.services import IngestionService, RAGService
from src.rag.dependencies import (
    get_rag_embedding_model,
    get_rag_llm,
    get_rag_prompt_template,
    get_rag_vector_store,
    get_text_splitter,
)
from src.rag.infrastructure.repositories import (
    SQLAlchemyChunkRepository,
    SQLAlchemyDocumentRepository,
)


class PerformanceMetrics:
    """A simple data class to hold our benchmark results."""

    def __init__(self) -> None:
        self.ingestion_time_seconds: float = 0.0
        self.query_latency_seconds: float = 0.0
        self.peak_ram_usage_mb: float = 0.0

    def __str__(self) -> str:
        return (
            f"\n--- Performance Benchmark Results ---\n"
            f"Document Ingestion Time: {self.ingestion_time_seconds:.2f} seconds\n"
            f"RAG Query Latency:       {self.query_latency_seconds:.2f} seconds\n"
            f"Peak RAM Usage:          {self.peak_ram_usage_mb:.2f} MB\n"
            f"-------------------------------------\n"
        )


def get_ram_usage_mb() -> float:
    """Returns the current RAM usage of the process in MB."""
    process = psutil.Process()
    memory_used: float = process.memory_info().rss / 1024**2
    return memory_used


def main(doc_path: Path, query: str) -> None:
    """
    Runs the full ingestion and RAG pipeline and measures performance.
    """
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    import_models()

    metrics = PerformanceMetrics()
    db = SessionLocal()

    try:
        print("--- Seeding database with a dummy Teacher and Chat ---")
        DUMMY_USER_ID = 1
        DUMMY_CHAT_ID = 1

        # Check if user already exists to make the script re-runnable
        teacher_user = db.query(User).filter(User.id == DUMMY_USER_ID).first()
        if not teacher_user:
            teacher_user = User(
                id=DUMMY_USER_ID,
                name="Benchmark Teacher",
                email="teacher@test.com",
                hashed_password="fake",
                role="teacher",
            )
            db.add(teacher_user)

        # Check if chat already exists
        benchmark_chat = db.query(Chat).filter(Chat.id == DUMMY_CHAT_ID).first()
        if not benchmark_chat:
            benchmark_chat = Chat(
                id=DUMMY_CHAT_ID, name="Benchmark Chat", owner_id=DUMMY_USER_ID
            )
            db.add(benchmark_chat)

        db.commit()
        print("Seeding complete.")

        print("\n--- Initializing services ---")
        embedding_model = get_rag_embedding_model()
        llm = get_rag_llm()
        prompt = get_rag_prompt_template()
        text_splitter = get_text_splitter()
        vector_store = get_rag_vector_store(embedding_model)

        doc_repo = SQLAlchemyDocumentRepository(db)
        chunk_repo = SQLAlchemyChunkRepository(db)
        chat_repo = SQLAlchemyChatRepository(db)

        ingestion_service = IngestionService(
            db=db,
            vector_store=vector_store,
            text_splitter=text_splitter,
            doc_repo=doc_repo,
            chunk_repo=chunk_repo,
            chat_repo=chat_repo,
        )
        rag_service = RAGService(llm, vector_store, prompt, chat_repo)
        print("Services initialized.")

        print("\n--- Running Warm-up Query (to load models) ---")
        # The first call will be slow as models are loaded into memory.
        _ = rag_service.answer_query("Warm-up query", chat_id=0)
        print("Models are now loaded into memory.")

        print(f"\n--- Benchmarking Ingestion for '{doc_path.name}' ---")
        pdf_bytes = doc_path.read_bytes()

        start_time = time.time()
        ingestion_service.ingest_document(
            file_bytes=pdf_bytes, file_name=doc_path.name, chat_id=DUMMY_CHAT_ID
        )
        metrics.ingestion_time_seconds = time.time() - start_time
        print("Ingestion complete.")

        print("\n--- Benchmarking RAG Query ---")
        print(f"Query: '{query}'")

        start_time = time.time()
        answer = rag_service.answer_query(query, chat_id=DUMMY_CHAT_ID)
        metrics.query_latency_seconds = time.time() - start_time
        print(f"Answer: {answer}")

        metrics.peak_ram_usage_mb = get_ram_usage_mb()
        print(metrics)

    except FileNotFoundError:
        print(f"Error: The document at '{doc_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark the ProVAI RAG pipeline.")
    parser.add_argument(
        "--doc-path",
        type=Path,
        required=True,
        help="Path to the PDF document to ingest.",
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="The query to ask the RAG pipeline.",
    )
    args = parser.parse_args()

    main(args.doc_path, args.query)
