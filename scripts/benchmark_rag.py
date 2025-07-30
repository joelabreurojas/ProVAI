"""
A simple script to measure the performance of the RAG pipeline.

python -m scripts.benchmark_rag --doc_path "/path/to/doc" --query "What's the topic?"
"""

import argparse
import logging
import time
from pathlib import Path

import psutil

from src.core.dependencies import (
    get_rag_embedding_model,
    get_rag_llm,
    get_rag_prompt_template,
    get_rag_vector_store,
    get_text_splitter,
)
from src.rag.application.services import IngestionService, RAGService


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
    memory_info: float = process.memory_info().rss / 1024**2

    return memory_info


def main(doc_path: Path, query: str) -> None:
    """
    Runs the full ingestion and RAG pipeline and measures performance.
    """
    # Configure logging to print to the console
    logging.basicConfig(level=logging.INFO)

    metrics = PerformanceMetrics()
    print("Initializing services...")

    embedding_model = get_rag_embedding_model()
    llm = get_rag_llm()
    prompt = get_rag_prompt_template()
    text_splitter = get_text_splitter()
    vector_store = get_rag_vector_store(embedding_model)

    ingestion_service = IngestionService(vector_store, text_splitter)
    rag_service = RAGService(llm, vector_store, prompt)
    print("Services initialized.")

    print("\n--- Running Warm-up Query (to load models) ---")

    # The first call will be slow as models are loaded into memory.
    _ = rag_service.answer_query("Warm-up query", chat_id=0)
    print("Models are now loaded into memory.")

    print(f"\n--- Benchmarking Ingestion for '{doc_path.name}' ---")
    try:
        pdf_bytes = doc_path.read_bytes()
    except FileNotFoundError:
        print(f"Error: The document at '{doc_path}' was not found.")
        return

    start_time = time.time()
    ingestion_service.ingest_document(
        file_bytes=pdf_bytes, file_name=doc_path.name, chat_id=1
    )
    metrics.ingestion_time_seconds = time.time() - start_time
    print("Ingestion complete.")

    print("\n--- Benchmarking RAG Query ---")
    print(f"Query: '{query}'")

    start_time = time.time()
    answer = rag_service.answer_query(query, chat_id=1)
    metrics.query_latency_seconds = time.time() - start_time
    print(f"Answer: {answer}")

    metrics.peak_ram_usage_mb = get_ram_usage_mb()
    print(metrics)


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
