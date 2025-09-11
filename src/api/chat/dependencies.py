from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.chat.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
)
from src.api.chat.application.services import ChatService
from src.api.chat.infrastructure.repositories import SQLAlchemyChatRepository
from src.api.rag.application.protocols import (
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.api.rag.dependencies import get_ingestion_service, get_rag_service
from src.api.tutor.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.api.tutor.dependencies import get_tutor_repository, get_tutor_service
from src.core.infrastructure.database import get_db


def get_chat_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> ChatRepositoryProtocol:
    return SQLAlchemyChatRepository(db)


def get_chat_service(
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
    rag_service: RAGServiceProtocol = Depends(get_rag_service),
    ingestion_service: IngestionServiceProtocol = Depends(get_ingestion_service),
    tutor_repo: TutorRepositoryProtocol = Depends(get_tutor_repository),
) -> ChatServiceProtocol:
    """
    Assembles the master ChatService orchestrator with all its required
    dependencies from other feature modules.
    """
    return ChatService(
        chat_repo=chat_repo,
        tutor_service=tutor_service,
        rag_service=rag_service,
        ingestion_service=ingestion_service,
        tutor_repo=tutor_repo,
    )
