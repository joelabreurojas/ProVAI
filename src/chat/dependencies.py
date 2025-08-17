from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.chat.application.protocols import (
    ChatRepositoryProtocol,
    SessionRepositoryProtocol,
    SessionServiceProtocol,
)
from src.chat.application.services import SessionService
from src.chat.infrastructure.repositories import (
    SQLAlchemyChatRepository,
    SQLAlchemySessionRepository,
)
from src.core.infrastructure.database import get_db


# --- Protocol Implementations ---
def get_chat_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> ChatRepositoryProtocol:
    return SQLAlchemyChatRepository(db)


def get_session_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> SessionRepositoryProtocol:
    return SQLAlchemySessionRepository(db)


# --- Service Assemblers ---
def get_session_service(
    session_repo: SessionRepositoryProtocol = Depends(get_session_repository),
) -> SessionServiceProtocol:
    return SessionService(session_repo=session_repo)
