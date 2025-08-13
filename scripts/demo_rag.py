"""
A headless script to run a full, end-to-end test of the ProVAI RAG engine.

This is an invaluable tool for debugging and demonstration, simulating the core
workflow of ingestion and querying using the application's pure builder functions.

Example:
    python -m scripts.demo_rag \\
        --doc-path "sample_data/scipy-lectures.pdf" \\
        --query "What is NumPy?"
"""

import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv

from src.chat.dependencies import build_history_service
from src.core.modules import import_models
from src.rag.dependencies import build_ingestion_service, build_rag_service


def main(doc_path: Path, query: str) -> None:
    """Runs a full, end-to-end test of the RAG pipeline."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    import_models()
    print("--- ProVAI Headless Demo ---")

    try:
        print(f"\n--- Ingesting Document: '{doc_path.name}' ---")
        ingestion_service = build_ingestion_service()
        pdf_bytes = doc_path.read_bytes()
        ingestion_service.ingest_document(
            file_bytes=pdf_bytes, file_name=doc_path.name, chat_id=1
        )
        print("Ingestion complete.")

        print("\n--- Querying RAG Engine ---")
        print(f"Query: '{query}'")
        rag_service = build_rag_service()
        history_service = build_history_service()

        answer = rag_service.answer_query(query, chat_id=1)
        print(f"\nAnswer:\n{answer}")

        # --- 3. Log the Interaction ---
        print("\n--- Logging interaction to history ---")
        history_service.log_interaction(
            chat_id=1,
            user_id=1,  # Using a dummy user_id for the script
            query=query,
            response=answer,
        )
        print("Interaction logged successfully.")

    except FileNotFoundError:
        print(f"❌ ERROR: The document at '{doc_path}' was not found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        # Re-raise to see the full traceback during debugging
        raise e
    finally:
        print("\n--- Demo Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a headless demo of the ProVAI RAG pipeline."
    )
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
