"""
A dedicated script for benchmarking the performance of the ProVAI RAG engine.

This script runs the full ingestion and querying pipeline and measures key
performance indicators: latency, memory usage, and throughput.

Example:
    python -m scripts.benchmark_rag \\
        --doc-path "sample_data/scipy-lectures.pdf" \\
        --query "What is NumPy?"
"""

import argparse
import logging
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv

from src.core.modules import import_models
from src.rag.dependencies import build_ingestion_service, build_rag_service


class PerformanceMetrics:
    """A simple data class to hold benchmark results."""

    ingestion_time_s: float = 0.0
    peak_ram_ingestion_mb: float = 0.0
    query_latency_s: float = 0.0
    peak_ram_query_mb: float = 0.0
    tokens_per_second: float = 0.0
    final_answer: str = ""


def get_ram_usage_mb() -> float:
    """Returns the current process's RAM usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024**2


def run_benchmark(doc_path: Path, query: str) -> PerformanceMetrics:
    """Runs the full pipeline and returns the performance metrics."""
    metrics = PerformanceMetrics()

    # Ingestion
    start_ram = get_ram_usage_mb()
    start_time = time.monotonic()
    ingestion_service = build_ingestion_service()
    pdf_bytes = doc_path.read_bytes()
    ingestion_service.ingest_document(
        file_bytes=pdf_bytes, file_name=doc_path.name, chat_id=1
    )

    metrics.ingestion_time_s = time.monotonic() - start_time
    end_ram_ingest = get_ram_usage_mb()
    metrics.peak_ram_ingestion_mb = end_ram_ingest - start_ram

    # Querying
    print("\n--- Initializing RAG Service ---")
    start_ram = get_ram_usage_mb()
    rag_service = build_rag_service()

    # This loads the model and builds the initial KV cache.
    _ = rag_service.answer_query("Warm-up query.", chat_id=1)
    print("Warm-up complete")

    # Now, we time the second query, which will be much faster.
    print("\n--- Running Timed Benchmark Query ---")
    start_time = time.monotonic()
    metrics.final_answer = rag_service.answer_query(query, chat_id=1)
    metrics.query_latency_s = time.monotonic() - start_time

    end_ram_query = get_ram_usage_mb()
    metrics.peak_ram_query_mb = end_ram_query - start_ram

    # Use the LangChain wrapper's built-in method to count tokens reliably.
    generated_tokens = rag_service.llm.get_num_tokens(metrics.final_answer)

    if metrics.query_latency_s > 0:
        metrics.tokens_per_second = generated_tokens / metrics.query_latency_s

    return metrics


def main(doc_path: Path, query: str) -> None:
    """Main function to run the benchmark and print results."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    import_models()
    print("--- ProVAI Performance Benchmark ---")

    try:
        metrics = run_benchmark(doc_path, query)

        print("\n--- Generated Answer ---")
        print(metrics.final_answer)

        print("\n--- Benchmark Results ---")
        print(f"{'Metric':<25} | {'Result':<15}")
        print(f"{'-' * 25} | {'-' * 15}")
        print(f"{'Ingestion Time (s)':<25} | {metrics.ingestion_time_s:<15.2f}")
        print(
            f"{'Peak RAM (Ingestion, MB)':<25} | {metrics.peak_ram_ingestion_mb:<15.2f}"
        )
        print(f"{'Query Latency (s)':<25} | {metrics.query_latency_s:<15.2f}")
        print(f"{'Peak RAM (Query, MB)':<25} | {metrics.peak_ram_query_mb:<15.2f}")
        print(f"{'Tokens per Second':<25} | {metrics.tokens_per_second:<15.2f}")
        print("-" * 43)

    except Exception as e:
        print(f"\n❌ An error occurred during benchmark: {e}")
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark the ProVAI RAG engine.")
    parser.add_argument("--doc-path", type=Path, required=True)
    parser.add_argument("--query", type=str, required=True)
    args = parser.parse_args()
    main(args.doc_path, args.query)
