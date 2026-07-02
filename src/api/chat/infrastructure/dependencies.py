from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.chat.application.services import ChatOrchestratorService
from src.api.chat.infrastructure.repositories import SQLAlchemyChatRepository
from src.api.tutor.infrastructure.dependencies import (
    get_tutor_repository,
    get_tutor_service,
)
from src.core.application.protocols import (
    ChatOrchestratorServiceProtocol,
    ChatRepositoryProtocol,
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.core.infrastructure.database import get_db
from src.core.infrastructure.utils import provides


@provides(ChatRepositoryProtocol)
def get_chat_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> ChatRepositoryProtocol:
    return SQLAlchemyChatRepository(db)


@provides(ChatOrchestratorServiceProtocol)
def get_chat_orchestrator_service(
    chat_repo: ChatRepositoryProtocol = Depends(get_chat_repository),
    tutor_repo: TutorRepositoryProtocol = Depends(get_tutor_repository),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> ChatOrchestratorServiceProtocol:
    """
    Assembles the master ChatOrchestratorService with all its required
    dependencies from other feature modules.
    """
    return ChatOrchestratorService(
        chat_repo=chat_repo,
        tutor_service=tutor_service,
        tutor_repo=tutor_repo,
    )
