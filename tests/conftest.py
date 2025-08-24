import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from langchain_chroma import Chroma
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

os.environ["ENV_STATE"] = "test"

from src.ai.application.services import EmbeddingService
from src.core.app import create_app
from src.core.infrastructure.database import Base, get_db
from src.core.infrastructure.settings import settings
from src.rag.dependencies import get_rag_vector_store

# The connect_args is specific to SQLite and is necessary
# to allow the database connection to be shared across different threads.
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[SQLAlchemySession, None, None]:
    """
    Provides a clean, transactional relational database session for each test.
    It creates and drops all tables for perfect isolation.
    """
    # Create all tables required by the models.
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

        # Drop all tables to ensure a clean state for the next test.
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def embedding_service() -> EmbeddingService:
    """Provides a single, session-scoped embedding service instance."""
    return EmbeddingService()


@pytest.fixture(scope="function")
def test_vector_store(embedding_service: EmbeddingService) -> Chroma:
    """
    It creates a ChromaDB instance in a temporary directory that is automatically
    cleaned up by pytest after the test runs.
    """
    tmp_dir = Path(f"/tmp/pytest-of-{os.getuid()}/pytest-current")
    test_store_path = tmp_dir / "test_vector_store"

    embedding_model = embedding_service.get_embedding_model()

    vector_store = Chroma(
        persist_directory=str(test_store_path),
        embedding_function=embedding_model,
    )
    return vector_store


@pytest.fixture(scope="function")
def app_and_client(
    db_session: SQLAlchemySession, test_vector_store: Chroma
) -> Generator[tuple[FastAPI, TestClient], None, None]:
    """
    Provides a configured FastAPI app instance and a TestClient for that app.
    This pattern allows tests to have a correctly typed handle to the app
    for managing dependency overrides.
    """
    app = create_app()

    # Define overrides before yielding
    def override_get_db() -> Generator[SQLAlchemySession, None, None]:
        yield db_session

    def override_get_vector_store() -> Chroma:
        return test_vector_store

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_rag_vector_store] = override_get_vector_store

    with TestClient(app) as test_client:
        yield app, test_client

    # Idempotent cleanup of all potential overrides
    app.dependency_overrides.clear()
