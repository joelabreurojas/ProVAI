import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from langchain_chroma import Chroma
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

os.environ["ENV_STATE"] = "test"

from src.ai.application.services import EmbeddingService
from src.ai.dependencies import get_embedding_service, get_llm_service
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
def client(
    db_session: SQLAlchemySession, test_vector_store: Chroma
) -> Generator[TestClient, None, None]:
    """
    Provides a FastAPI TestClient that is configured to use the clean,
    transactional test database session.
    """
    app = create_app()

    def override_get_db() -> Generator[SQLAlchemySession, None, None]:
        yield db_session

    def override_get_vector_store() -> Chroma:
        return test_vector_store

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_rag_vector_store] = override_get_vector_store

    with TestClient(app) as test_client:
        yield test_client

    # Idempotent cleanup of all potential overrides
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_rag_vector_store, None)
    app.dependency_overrides.pop(get_llm_service, None)
    app.dependency_overrides.pop(get_embedding_service, None)
