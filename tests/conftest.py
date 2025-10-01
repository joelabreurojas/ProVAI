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
from pytest_mock import MockerFixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker

os.environ["ENV_STATE"] = "test"

from src.api.ai.infrastructure.dependencies import (
    get_embedding_service,
    get_llm_service,
)
from src.api.rag.infrastructure.dependencies import get_rag_vector_store
from src.core.infrastructure.app import create_app
from src.core.infrastructure.database import Base, get_db
from src.core.infrastructure.settings import settings
from src.ui.shared.infrastructure.dependencies import (
    get_authenticated_bff_api_client,
    get_unauthenticated_bff_api_client,
)

# The connect_args is specific to SQLite for multithreaded access in tests.
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[SQLAlchemySession, None, None]:
    """
    Provides a clean, transactional relational database session for each test.
    It creates and drops all tables for perfect isolation.
    """
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
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_vector_store() -> Generator[Chroma, None, None]:
    """
    Provides a clean, isolated ChromaDB instance for each test in a temporary
    directory that is automatically cleaned up.
    """
    # This path is robust for different OS and user environments
    tmp_dir = Path(f"/tmp/pytest-of-{os.getuid()}/pytest-current")
    test_store_path = tmp_dir / f"test_vector_store_{os.urandom(8).hex()}"
    test_store_path.parent.mkdir(parents=True, exist_ok=True)

    # We need a real embedding model to initialize ChromaDB, but it's session-scoped
    # so it's only loaded once per test run.
    from src.api.ai.application.services import EmbeddingService

    embedding_service = EmbeddingService()
    embedding_model = embedding_service.get_embedding_model()

    vector_store = Chroma(
        persist_directory=str(test_store_path),
        embedding_function=embedding_model,
    )
    try:
        yield vector_store
    finally:
        # Cleanup the temporary directory
        if test_store_path.exists():
            shutil.rmtree(test_store_path)


@pytest.fixture(scope="function")
def app(
    db_session: SQLAlchemySession,
    test_vector_store: Chroma,
    mocker: MockerFixture,
) -> Generator[FastAPI, None, None]:
    """
    The single, definitive application fixture. It creates one app instance per
    test and applies all necessary overrides for a fully isolated E2E test
    environment. AI services are mocked by default for speed.
    """
    # Clear singleton caches to ensure test isolation
    from src.api.ai.application.services.embedding_service import (
        _load_embedding_model_singleton,
    )
    from src.api.ai.application.services.llm_service import _load_llm_singleton

    _load_llm_singleton.cache_clear()
    _load_embedding_model_singleton.cache_clear()

    # Create the FastAPI app instance
    app = create_app()

    # Override database and vector store dependencies
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_rag_vector_store] = lambda: test_vector_store

    # Override BFF clients to use the in-memory TestClient transport
    transport = httpx.ASGITransport(app=app)
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

    # Mock AI services by default for fast, isolated tests
    mock_llm_service = mocker.MagicMock()
    mock_embedding_service = mocker.MagicMock()
    app.dependency_overrides[get_llm_service] = lambda: mock_llm_service
    app.dependency_overrides[get_embedding_service] = lambda: mock_embedding_service

    yield app

    # Cleanup is handled automatically by the fixture's teardown
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """
    The single, definitive TestClient fixture. All E2E tests should use this.
    It automatically uses the configured `app` fixture for the current test.
    """
    with TestClient(app) as test_client:
        yield test_client
