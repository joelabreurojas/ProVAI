from fastapi import Depends
from sqlalchemy.orm import Session

from src.chat.application.protocols import (
    HistoryRepositoryProtocol,
    HistoryServiceProtocol,
)
from src.chat.application.services import HistoryService
from src.chat.infrastructure.repositories import SQLAlchemyHistoryRepository
from src.core.infrastructure.database import SessionLocal, get_db

# --- Builder Functions (No FastAPI) ---


def build_history_repository() -> HistoryRepositoryProtocol:
    """Builds a history repository with its own database session."""
    db = SessionLocal()
    return SQLAlchemyHistoryRepository(db)


def build_history_service() -> HistoryServiceProtocol:
    """Constructs the HistoryService with all its real dependencies."""
    history_repo = build_history_repository()
    return HistoryService(history_repo=history_repo)


# --- FastAPI Dependency Providers ---


def get_history_repository(db: Session = Depends(get_db)) -> HistoryRepositoryProtocol:
    """FastAPI dependency provider for the HistoryRepository."""
    return SQLAlchemyHistoryRepository(db)


def get_history_service(
    history_repo: HistoryRepositoryProtocol = Depends(get_history_repository),
) -> HistoryServiceProtocol:
    """FastAPI dependency provider for the HistoryService."""
    return HistoryService(history_repo=history_repo)
