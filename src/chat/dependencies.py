from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.chat.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
)
from src.chat.application.services import ChatService
from src.chat.infrastructure.repositories import SQLAlchemyChatRepository
from src.core.infrastructure.database import get_db
from src.rag.application.protocols import (
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.rag.dependencies import get_ingestion_service, get_rag_service
from src.tutor.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.tutor.dependencies import get_tutor_repository, get_tutor_service


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
