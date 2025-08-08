from fastapi import Depends
from sqlalchemy.orm import Session

from src.chat.application.protocols import (
    HistoryRepositoryProtocol,
    HistoryServiceProtocol,
)
from src.chat.application.services import HistoryService
from src.chat.infrastructure.repositories import SQLAlchemyHistoryRepository
from src.core.infrastructure.database import get_db


# --- Protocol Implementations for Chat ---
def get_history_repository(db: Session = Depends(get_db)) -> HistoryRepositoryProtocol:
    return SQLAlchemyHistoryRepository(db)


# --- Service Assembler for Chat ---
def get_history_service(
    history_repo: HistoryRepositoryProtocol = Depends(get_history_repository),
) -> HistoryServiceProtocol:
    return HistoryService(history_repo=history_repo)
