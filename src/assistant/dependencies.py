from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.assistant.application.protocols import (
    AssistantRepositoryProtocol,
    ChatRepositoryProtocol,
    ChatServiceProtocol,
)
from src.assistant.application.services import ChatService
from src.assistant.infrastructure.repositories import (
    SQLAlchemyAssistantRepository,
    SQLAlchemyChatRepository,
)
from src.core.infrastructure.database import get_db


# --- Protocol Implementations ---
def get_assistant_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> AssistantRepositoryProtocol:
    return SQLAlchemyAssistantRepository(db)


def get_chat_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> ChatRepositoryProtocol:
    return SQLAlchemyChatRepository(db)


# --- Service Assemblers ---
def get_chat_service(
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
) -> ChatServiceProtocol:
    return ChatService(chat_repo=chat_repo)
