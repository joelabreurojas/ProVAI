"""
A simple script to measure the performance of the RAG pipeline.

This script seeds the database, runs a warm-up query to load AI models,
and then benchmarks the ingestion and query processes.

Example:
python -m scripts.benchmark_rag --doc-path "sample_data/attention_is_all_you_need.pdf" \
--query "What is a multi-head self-attention mechanism?"
"""

import argparse
import logging
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ai.application.services import EmbeddingService, LLMService
from src.auth.domain.models import User
from src.core.infrastructure.database import SessionLocal
from src.core.modules import import_models
from src.rag.application.prompts import get_rag_prompt
from src.rag.application.services import IngestionService, RAGService
from src.rag.infrastructure.repositories import (
    SQLAlchemyChunkRepository,
    SQLAlchemyDocumentRepository,
)
from src.rag.infrastructure.vector_store import get_vector_store
from src.tutor.domain.models import Tutor
from src.tutor.infrastructure.repositories import SQLAlchemyTutorRepository


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
        print("--- Seeding database with a dummy Teacher and Tutor ---")
        DUMMY_USER_ID = 1
        DUMMY_TUTOR_ID = 1

        teacher_user = db.query(User).filter(User.id == DUMMY_USER_ID).first()
        if not teacher_user:
            db.add(
                User(
                    id=DUMMY_USER_ID,
                    name="Benchmark Teacher",
                    email="teacher@benchmark.com",
                    hashed_password="fake",
                    role="teacher",
                )
            )

        benchmark_tutor = db.query(Tutor).filter(Tutor.id == DUMMY_TUTOR_ID).first()
        if not benchmark_tutor:
            db.add(
                Tutor(
                    id=DUMMY_TUTOR_ID,
                    name="Benchmark Tutor",
                    teacher_id=DUMMY_USER_ID,
                )
            )

        db.commit()
        print("Seeding complete.")

        print("\n--- Initializing services ---")
        llm_service = LLMService()
        embedding_service = EmbeddingService()
        llm = llm_service.get_llm()
        embedding_model = embedding_service.get_embedding_model()
        vector_store = get_vector_store(embedding_model)
        prompt = get_rag_prompt()
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=300, chunk_overlap=0, encoding_name="cl100k_base"
        )
        doc_repo = SQLAlchemyDocumentRepository(db)
        chunk_repo = SQLAlchemyChunkRepository(db)
        tutor_repo = SQLAlchemyTutorRepository(db)

        ingestion_service = IngestionService(
            db=db,
            vector_store=vector_store,
            text_splitter=text_splitter,
            doc_repo=doc_repo,
            chunk_repo=chunk_repo,
            tutor_repo=tutor_repo,
        )
        rag_service = RAGService(
            llm=llm,
            vector_store=vector_store,
            prompt=prompt,
            tutor_repo=tutor_repo,
        )
        print("Services initialized.")

        print("\n--- Running Warm-up Query (to load models) ---")
        _ = rag_service.answer_query("Warm-up query", tutor_id=0)
        print("Models are now loaded into memory.")

        print(f"\n--- Benchmarking Ingestion for '{doc_path.name}' ---")
        pdf_bytes = doc_path.read_bytes()
        start_time = time.time()
        ingestion_service.ingest_document(
            file_bytes=pdf_bytes,
            file_name=doc_path.name,
            tutor_id=DUMMY_TUTOR_ID,
        )
        metrics.ingestion_time_seconds = time.time() - start_time
        print("Ingestion complete.")

        print("\n--- Benchmarking RAG Query ---")
        print(f"Query: '{query}'")
        start_time = time.time()
        answer = rag_service.answer_query(query, tutor_id=DUMMY_TUTOR_ID)
        metrics.query_latency_seconds = time.time() - start_time
        print(f"Answer:\n{answer}")

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
