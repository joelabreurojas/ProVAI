"""
A headless script to run a full, end-to-end demo of the ProVAI RAG engine.

This script simulates the definitive, decoupled user workflow. It is a practical
demonstration of how the ChatService orchestrates all other feature modules.

Example:
python -m scripts.demo_rag
"""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.ai.infrastructure.dependencies import (
    get_embedding_service,
    get_llm_service,
)
from src.api.auth.infrastructure.dependencies import (
    get_auth_service,
    get_password_service,
    get_token_service,
    get_user_repository,
)
from src.api.chat.infrastructure.dependencies import (
    get_chat_repository,
    get_chat_service,
)
from src.api.rag.infrastructure.dependencies import (
    get_chunk_repository,
    get_document_repository,
    get_ingestion_service,
    get_rag_prompt_template,
    get_rag_service,
    get_rag_vector_store,
    get_text_splitter,
)
from src.api.tutor.infrastructure.dependencies import (
    get_tutor_repository,
    get_tutor_service,
)
from src.core.application.protocols import AuthServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import TutorCreate
from src.core.infrastructure.database import SessionLocal
from src.core.infrastructure.settings import settings
from src.core.infrastructure.utils import import_core_models

SAMPLE_DOC_PATH = Path("sample_data/attention_is_all_you_need.pdf")
SAMPLE_QUERY = "What is a multi-head self-attention mechanism?"
VALID_PASSWORD = "ValidPassword123!"


class AppContainer:
    """A container to manually assemble and hold our application services."""

    def __init__(self, db_session: SQLAlchemySession) -> None:
        # Repositories ---
        self.user_repo = get_user_repository(db_session)
        self.tutor_repo = get_tutor_repository(db_session)
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
    new_user = auth_service.register_user(name=name, email=email, password=password)
    if role:
        new_user.role = role
        db_session.commit()
        db_session.refresh(new_user)
    return new_user


def main() -> None:
    """Runs a full, end-to-end demo of the headless RAG pipeline."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    import_core_models()

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

    print("--- ProVAI Headless Demo ---")
    db = SessionLocal()

    try:
        print("--- Assembling services...")
        container = AppContainer(db)
        print("--- Services assembled successfully.")

        print("\n--- Seeding database with a Teacher and a Student ---")
        teacher = get_or_create_user(
            auth_service=container.auth_service,
            db_session=db,
            name="Demo Teacher",
            email="teacher@demo.com",
            password=VALID_PASSWORD,
            role="teacher",
        )
        student = get_or_create_user(
            auth_service=container.auth_service,
            db_session=db,
            name="Demo Student",
            email="student@demo.com",
            password=VALID_PASSWORD,
            role="student",
        )
        print(f"Using Teacher (ID: {teacher.id}) and Student (ID: {student.id}).")

        print("\n--- Teacher creates a new Tutor ---")
        tutor = container.tutor_service.create_tutor(
            TutorCreate(course_name="Demo AI Course"), teacher=teacher
        )
        print(f"Tutor '{tutor.course_name}' created with ID: {tutor.id}.")

        invitation_response = container.tutor_service.add_students_to_invitation(
            tutor_id=tutor.id,
            requesting_user=teacher,
            student_emails=["student@demo.com"],
        )
        invitation_token = invitation_response.invitation_token

        if not invitation_token:
            raise ValueError("Failed to create a valid invitation token.")
        print("Invitation token generated.")

        print("\n--- Student enrolls in the Tutor using the token ---")
        container.tutor_service.enroll_student_from_token(
            token=invitation_token, student_user=student
        )
        print(f"Student {student.id} successfully enrolled in Tutor {tutor.id}.")

        print("\n--- Student creates their own Chat with the Tutor ---")
        student_chat = container.chat_service.create_new_chat(
            tutor_id=tutor.id, user=student, title=f"Chat about {SAMPLE_DOC_PATH.name}"
        )
        print(f"Student Chat created with ID: {student_chat.id}.")

        print(f"\n--- Teacher uploads document '{SAMPLE_DOC_PATH.name}' ---")
        pdf_bytes = SAMPLE_DOC_PATH.read_bytes()
        container.chat_service.add_document_to_chat(
            chat_id=student_chat.id,
            file_bytes=pdf_bytes,
            file_name=SAMPLE_DOC_PATH.name,
            current_user=teacher,
        )
        print("Document uploaded and ingested successfully.")

        print("\n--- Student asks a question in a chat ---")
        print(f"Query: '{SAMPLE_QUERY}'")
        answer = container.chat_service.post_message(
            chat_id=student_chat.id, query=SAMPLE_QUERY, current_user=student
        )
        print(f"\nAI Answer:\n{answer}")

        print("\n--- Verifying interaction was logged to history ---")
        history = container.chat_service.get_history(
            chat_id=student_chat.id, user=student
        )
        assert len(history) == 2
        assert history[0].role == "user" and history[0].content == SAMPLE_QUERY
        assert history[1].role == "tutor" and history[1].content == answer
        print("History verified successfully.")

    except FileNotFoundError:
        print(f"Error: The document at '{SAMPLE_DOC_PATH}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise e
    finally:
        db.close()
        print("\n--- Demo Complete ---")


if __name__ == "__main__":
    main()
