"""
A script to measure the performance of the core, orchestrator-driven RAG pipeline.

This script simulates the most critical user actions and measures their performance,
including a warm-up phase to ensure AI models are pre-loaded.

Example:
python -m scripts.benchmark_rag \
--doc-path "sample_data/attention_is_all_you_need.pdf" \
--query "What is a multi-head self-attention mechanism?"
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv
from sqlalchemy.orm import Session as SQLAlchemySession

from src.ai.dependencies import get_embedding_service, get_llm_service
from src.auth.application.protocols import AuthServiceProtocol
from src.auth.dependencies import (
    get_auth_service,
    get_password_service,
    get_token_service,
    get_user_repository,
)
from src.auth.domain.models import User
from src.auth.domain.schemas import UserCreate
from src.chat.dependencies import get_chat_repository, get_chat_service
from src.core.infrastructure.database import SessionLocal
from src.core.infrastructure.settings import settings
from src.core.modules import import_models
from src.rag.dependencies import (
    get_chunk_repository,
    get_document_repository,
    get_ingestion_service,
    get_rag_prompt_template,
    get_rag_service,
    get_rag_vector_store,
    get_text_splitter,
)
from src.tutor.dependencies import (
    get_invitation_repository,
    get_tutor_repository,
    get_tutor_service,
)
from src.tutor.domain.schemas import TutorCreate

VALID_PASSWORD = "ValidPassword123!"


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


class AppContainer:
    """A container to manually assemble and hold our application services."""

    def __init__(self, db_session: SQLAlchemySession) -> None:
        # Repositories ---
        self.user_repo = get_user_repository(db_session)
        self.tutor_repo = get_tutor_repository(db_session)
        self.invitation_repo = get_invitation_repository(db_session)
        self.chat_repo = get_chat_repository(db_session)
        self.doc_repo = get_document_repository(db_session)
        self.chunk_repo = get_chunk_repository(db_session)

        # Infrastructure
        self.token_service = get_token_service()
        self.password_service = get_password_service()
        self.llm_service = get_llm_service()
        self.embedding_service = get_embedding_service()
        self.vector_store = get_rag_vector_store(self.embedding_service)
        self.text_splitter = get_text_splitter()
        self.rag_prompt = get_rag_prompt_template()

        # Services
        self.auth_service = get_auth_service(
            user_repo=self.user_repo,
            password_svc=self.password_service,
            token_svc=self.token_service,
        )
        self.tutor_service = get_tutor_service(
            tutor_repo=self.tutor_repo,
            invitation_repo=self.invitation_repo,
        )
        self.ingestion_service = get_ingestion_service(
            db=db_session,
            vector_store=self.vector_store,
            text_splitter=self.text_splitter,
            doc_repo=self.doc_repo,
            chunk_repo=self.chunk_repo,
        )
        self.rag_service = get_rag_service(
            llm_service=self.llm_service,
            vector_store=self.vector_store,
            prompt=self.rag_prompt,
        )

        # The Orchestrator
        self.chat_service = get_chat_service(
            chat_repo=self.chat_repo,
            tutor_service=self.tutor_service,
            rag_service=self.rag_service,
            ingestion_service=self.ingestion_service,
            tutor_repo=self.tutor_repo,
        )


def get_or_create_user(
    auth_service: AuthServiceProtocol,
    db_session: SQLAlchemySession,
    name: str,
    email: str,
    password: str,
    role: str | None = None,
) -> User:
    """Gets a user by email, or creates them if they don't exist."""
    user = auth_service.get_user_by_email(email)
    if user:
        print(f"User '{email}' already exists, using existing user.")
        # Ensure role is correct
        if role and user.role != role:
            user.role = role
            db_session.commit()
            db_session.refresh(user)
        return user

    print(f"Creating new user: '{email}'...")
    new_user = auth_service.register_user(
        UserCreate(name=name, email=email, password=password)
    )
    if role:
        new_user.role = role
        db_session.commit()
        db_session.refresh(new_user)
    return new_user


def main(doc_path: Path, query: str) -> None:
    """Runs the full pipeline and measures performance."""

    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    import_models()

    if settings.ENV_STATE != "dev":
        print(
            "\n❌ ERROR: This script is destructive and is designed to run "
            "only in a 'dev' environment."
        )
        print(
            f"Current ENV_STATE is '{settings.ENV_STATE}'. "
            "Aborting to prevent data loss."
        )
        sys.exit(1)

    print(f"--- Using development database: {settings.DB_URL} ---")
    metrics = PerformanceMetrics()
    db = SessionLocal()

    try:
        # Assemble dependencies
        container = AppContainer(db)

        # Seed database
        teacher = get_or_create_user(
            auth_service=container.auth_service,
            db_session=db,
            name="Benchmark Teacher",
            email="teacher@benchmark.com",
            password=VALID_PASSWORD,
            role="teacher",
        )
        student = get_or_create_user(
            auth_service=container.auth_service,
            db_session=db,
            name="Benchmark Student",
            email="student@benchmark.com",
            password=VALID_PASSWORD,
            role="student",
        )

        tutor = container.tutor_service.create_tutor(
            TutorCreate(course_name="Benchmark Course"),
            teacher=teacher,
        )

        invitation_response = container.tutor_service.add_students_to_invitation(
            tutor_id=tutor.id,
            requesting_user=teacher,
            student_emails=["student@benchmark.com"],
        )

        invitation_token = invitation_response.invitation_token
        if not invitation_token:
            raise ValueError("Failed to create invitation token for benchmark.")

        container.tutor_service.enroll_student_from_token(
            token=invitation_token, student_user=student
        )

        student_chat = container.chat_service.create_new_chat(
            tutor.id, user=student, title="Benchmark Chat"
        )

        # Warm-up Phase
        print("\n--- Running Warm-up Query (to load models) ---")
        _ = container.chat_service.post_message(
            chat_id=student_chat.id, query="Warm-up", current_user=student
        )
        print("Models are now loaded into memory.")

        # Benchmark Ingestion
        print(f"\n--- Benchmarking Ingestion for '{doc_path.name}' ---")
        pdf_bytes = doc_path.read_bytes()
        start_time = time.time()
        container.chat_service.add_document_to_chat(
            chat_id=student_chat.id,
            file_bytes=pdf_bytes,
            file_name=doc_path.name,
            current_user=teacher,
        )
        metrics.ingestion_time_seconds = time.time() - start_time
        print("Ingestion complete.")

        # Benchmark Query
        print("\n--- Benchmarking RAG Query ---")
        print(f"Query: '{query}'")
        start_time = time.time()
        answer = container.chat_service.post_message(
            chat_id=student_chat.id, query=query, current_user=student
        )
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
        "--doc-path", type=Path, required=True, help="Path to the PDF document."
    )
    parser.add_argument(
        "--query", type=str, required=True, help="The query to ask the RAG pipeline."
    )
    args = parser.parse_args()
    main(args.doc_path, args.query)
