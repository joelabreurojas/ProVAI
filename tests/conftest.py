import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ["ENV_STATE"] = "test"

from src.core.app import create_app
from src.core.infrastructure.database import Base, get_db
from src.core.infrastructure.settings import settings

# The connect_args is specific to SQLite and is necessary
# to allow the database connection to be shared across different threads.
engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest.fixture
def dummy_model_path(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Creates a dummy, empty model file in a temporary directory for tests
    that need a model file to exist, but don't need to load it.
    """
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    models_dir = assets_dir / "models"
    models_dir.mkdir()
    dummy_file = models_dir / "dummy-model.gguf"
    dummy_file.touch()

    yield dummy_file
