from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.auth.application.protocols import TokenServiceProtocol, UserRepositoryProtocol
from src.auth.dependencies import get_token_service, get_user_repository
from src.chat.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
)
from src.chat.application.services import ChatService
from src.chat.infrastructure.repositories import SQLAlchemyChatRepository
from src.core.infrastructure.database import get_db
from src.tutor.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.tutor.application.services import TutorService
from src.tutor.infrastructure.repositories import SQLAlchemyTutorRepository


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
    user_repo: UserRepositoryProtocol = Depends(get_user_repository),
    token_service: TokenServiceProtocol = Depends(get_token_service),
) -> TutorServiceProtocol:
    return TutorService(
        tutor_repo=tutor_repo, user_repo=user_repo, token_service=token_service
    )


def get_chat_service(
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
) -> ChatServiceProtocol:
    return ChatService(chat_repo=chat_repo)
