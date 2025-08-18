"""
A headless script to run a full, end-to-end test of the ProVAI RAG engine.

This is an invaluable tool for debugging and demonstration before the UI is
fully implemented. It simulates the core workflow of ingestion and querying.

Example:
python -m scripts.demo_rag --doc-path "sample_data/attention_is_all_you_need.pdf" \
--query "What is a multi-head self-attention mechanism?"
"""

import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ai.application.services import EmbeddingService, LLMService
from src.auth.domain.models import User
from src.chat.application.services import SessionService
from src.chat.domain.models import Chat
from src.chat.infrastructure.repositories import (
    SQLAlchemyChatRepository,
    SQLAlchemySessionRepository,
)
from src.core.infrastructure.database import SessionLocal
from src.core.modules import import_models
from src.rag.application.prompts import get_rag_prompt
from src.rag.application.services import IngestionService, RAGService
from src.rag.infrastructure.repositories import (
    SQLAlchemyChunkRepository,
    SQLAlchemyDocumentRepository,
)
from src.rag.infrastructure.vector_store import get_vector_store


def main(doc_path: Path, query: str) -> None:
    """Runs a full, end-to-end test of the headless RAG pipeline."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    import_models()

    print("--- ProVAI Headless Demo ---")

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
                name="Demo Teacher",
                email="teacher@demo.com",
                hashed_password="fake",
                role="teacher",
            )
            db.add(teacher_user)

        # Check if chat already exists
        demo_chat = db.query(Chat).filter(Chat.id == DUMMY_CHAT_ID).first()
        if not demo_chat:
            demo_chat = Chat(id=DUMMY_CHAT_ID, name="Demo Chat", owner_id=DUMMY_USER_ID)
            db.add(demo_chat)

        db.commit()
        print("Seeding complete.")

        print("Initializing services...")
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
        chat_repo = SQLAlchemyChatRepository(db)
        session_repo = SQLAlchemySessionRepository(db)

        session_service = SessionService(session_repo=session_repo)
        ingestion_service = IngestionService(
            db=db,
            vector_store=vector_store,
            text_splitter=text_splitter,
            doc_repo=doc_repo,
            chunk_repo=chunk_repo,
            chat_repo=chat_repo,
        )
        rag_service = RAGService(
            llm=llm,
            vector_store=vector_store,
            prompt=prompt,
            chat_repo=chat_repo,
        )
        print("Services initialized.")

        print("\nCreating a new session for this demo...")
        session = session_service.get_or_create_session(
            chat_id=DUMMY_CHAT_ID, user_id=DUMMY_USER_ID
        )
        print(f"Using Session ID: {session.id}")

        print(f"\n--- Ingesting Document: '{doc_path.name}' ---")
        pdf_bytes = doc_path.read_bytes()
        ingestion_service.ingest_document(
            file_bytes=pdf_bytes, file_name=doc_path.name, chat_id=DUMMY_CHAT_ID
        )
        print("Ingestion complete.")

        print("\n--- Querying RAG Engine ---")
        print(f"Query: '{query}'")
        answer = rag_service.answer_query(query, chat_id=DUMMY_CHAT_ID)
        print(f"\nAnswer:\n{answer}")

        print("\n--- Logging interaction to history ---")
        session_service.log_interaction(
            session_id=session.id,
            user_query=query,
            assistant_response=answer,
        )
        print("Interaction logged successfully.")

    except FileNotFoundError:
        print(f"Error: The document at '{doc_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
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
