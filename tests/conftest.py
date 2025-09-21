import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Generator

import httpx
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from langchain_chroma import Chroma
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

os.environ["ENV_STATE"] = "test"

from src.api.ai.application.services import EmbeddingService
from src.api.ai.application.services.embedding_service import (
    _load_embedding_model_singleton,
)
from src.api.ai.application.services.llm_service import _load_llm_singleton
from src.api.rag.infrastructure.dependencies import get_rag_vector_store
from src.core.infrastructure.app import create_app
from src.core.infrastructure.database import Base, get_db
from src.core.infrastructure.settings import settings
from src.ui.shared.infrastructure.dependencies import (
    get_authenticated_bff_api_client,
    get_unauthenticated_bff_api_client,
)

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
def test_vector_store(
    embedding_service: EmbeddingService,
) -> Generator[Chroma, None, None]:
    """
    Provides a clean, isolated ChromaDB instance for each test.
    It creates a ChromaDB instance in a temporary directory and, crucially,
    deletes the entire directory after the test runs to prevent pollution.
    """
    tmp_dir = Path(f"/tmp/pytest-of-{os.getuid()}/pytest-current")
    test_store_path = tmp_dir / f"test_vector_store_{os.urandom(8).hex()}"

    test_store_path.parent.mkdir(parents=True, exist_ok=True)

    embedding_model = embedding_service.get_embedding_model()

    vector_store = Chroma(
        persist_directory=str(test_store_path),
        embedding_function=embedding_model,
    )

    try:
        yield vector_store
    finally:
        if test_store_path.exists():
            shutil.rmtree(test_store_path)


@pytest.fixture(scope="function")
def app(
    db_session: SQLAlchemySession, test_vector_store: Chroma
) -> Generator[FastAPI, None, None]:
    """
    Provides a fully configured application instance for testing,
    with all dependencies overridden.
    """
    app = create_app()

    transport = httpx.ASGITransport(app=app)

    # The base_url includes the API prefix for correct routing
    api_base_url = f"http://testserver{settings.API_ROOT_PATH}"

    @asynccontextmanager
    async def override_get_unauthenticated_bff_api_client() -> AsyncGenerator[
        httpx.AsyncClient, None
    ]:
        async with httpx.AsyncClient(
            transport=transport, base_url=api_base_url
        ) as client:
            yield client

    @asynccontextmanager
    async def override_get_authenticated_bff_api_client(
        request: Request,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        token = request.session.get("user_token")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        async with httpx.AsyncClient(
            transport=transport, base_url=api_base_url, headers=headers
        ) as client:
            yield client

    app.dependency_overrides[get_unauthenticated_bff_api_client] = (
        override_get_unauthenticated_bff_api_client
    )
    app.dependency_overrides[get_authenticated_bff_api_client] = (
        override_get_authenticated_bff_api_client
    )

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_rag_vector_store] = lambda: test_vector_store

    yield app

    # Idempotent cleanup of all potential overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """
    Provides a TestClient that is configured with the correct API base URL.
    This is the definitive client that all E2E tests should use.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def fresh_ai_services() -> Generator[None, None, None]:
    """
    A fixture that automatically clears the singleton caches for the AI services
    before every test runs. This is the definitive solution to test pollution
    from the session-scoped AI models.
    """
    _load_llm_singleton.cache_clear()
    _load_embedding_model_singleton.cache_clear()
    yield
