from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.auth.application.protocols import TokenServiceProtocol
from src.auth.dependencies import get_token_service
from src.core.infrastructure.database import get_db
from src.tutor.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.tutor.application.services import ChatService, TutorService
from src.tutor.infrastructure.repositories import (
    SQLAlchemyChatRepository,
    SQLAlchemyTutorRepository,
)


# --- Protocol Implementations ---
def get_tutor_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> TutorRepositoryProtocol:
    return SQLAlchemyTutorRepository(db)


def get_chat_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> ChatRepositoryProtocol:
    return SQLAlchemyChatRepository(db)


# --- Service Assemblers ---
def get_tutor_service(
    tutor_repo: TutorRepositoryProtocol = Depends(get_tutor_repository),
    token_service: TokenServiceProtocol = Depends(get_token_service),
) -> TutorServiceProtocol:
    return TutorService(tutor_repo=tutor_repo, token_service=token_service)


def get_chat_service(
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
) -> ChatServiceProtocol:
    return ChatService(chat_repo=chat_repo)
