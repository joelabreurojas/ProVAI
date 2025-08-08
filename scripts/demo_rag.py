"""
A headless script to run a full, end-to-end test of the ProVAI RAG engine.

python -m scripts.demo_rag --doc-path "sample_data/doc" --query ""

This script is an invaluable tool for debugging and demonstration before the UI
is fully implemented. It simulates the core workflow of ingestion and querying.
"""

import argparse
import logging
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.chat.application.services import HistoryService
from src.chat.infrastructure.repositories import SQLAlchemyHistoryRepository
from src.core.infrastructure.database import SessionLocal
from src.core.modules import import_models
from src.rag.application.prompts import get_rag_prompt
from src.rag.application.services.ingestion_service import IngestionService
from src.rag.application.services.rag_service import RAGService
from src.rag.infrastructure.model_loader import get_embedding_model, get_llm
from src.rag.infrastructure.vector_store import get_vector_store


def main(doc_path: Path, query: str) -> None:
    """Runs a full, end-to-end test of the headless RAG pipeline."""
    # See output from services.
    logging.basicConfig(level=logging.INFO)

    import_models()

    print("--- ProVAI Headless Demo ---")

    print("Initializing services...")
    db = SessionLocal()

    # Build low-level components by calling their providers or constructors.
    embedding_model = get_embedding_model()
    llm = get_llm()
    prompt = get_rag_prompt()
    vector_store = get_vector_store(embedding_model)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300, chunk_overlap=0, encoding_name="cl100k_base"
    )

    history_repo = SQLAlchemyHistoryRepository(db)

    # Manually construct the high-level application services with their dependencies.
    ingestion_service = IngestionService(
        vector_store=vector_store, text_splitter=text_splitter
    )
    rag_service = RAGService(llm=llm, vector_store=vector_store, prompt=prompt)
    history_service = HistoryService(history_repo=history_repo)
    print("Services initialized.")

    # In a real app, this would come from the authenticated user and their chat.
    DUMMY_CHAT_ID = 1
    DUMMY_USER_ID = 1
    print(f"Using dummy context: chat_id={DUMMY_CHAT_ID}, user_id={DUMMY_USER_ID}")

    try:
        print(f"\n--- Ingesting Document: '{doc_path.name}' ---")
        pdf_bytes = doc_path.read_bytes()
        ingestion_service.ingest_document(
            file_bytes=pdf_bytes, file_name=doc_path.name, chat_id=DUMMY_CHAT_ID
        )
        print("Ingestion complete.")

        print("\n--- Querying RAG Engine ---")
        print(f"Query: '{query}'")
        answer = rag_service.answer_query(query, chat_id=DUMMY_CHAT_ID)
        print(f"\nAnswer: {answer}")

        print("\n--- Logging interaction to history ---")
        history_service.log_interaction(
            chat_id=DUMMY_CHAT_ID,
            user_id=DUMMY_USER_ID,
            query=query,
            response=answer,
        )
        print("Interaction logged successfully.")

    except FileNotFoundError:
        print(f"Error: The document at '{doc_path}' was not found.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Re-raise for debugging purposes if needed
        # raise
    finally:
        db.close()
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
