from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.tutor.application.services import TutorService
from src.api.tutor.infrastructure.repositories import SQLAlchemyTutorRepository
from src.core.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.core.infrastructure.database import get_db
from src.core.infrastructure.utils import provides


@provides(TutorRepositoryProtocol)
def get_tutor_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> TutorRepositoryProtocol:
    return SQLAlchemyTutorRepository(db)


@provides(TutorServiceProtocol)
def get_tutor_service(
    tutor_repo: TutorRepositoryProtocol = Depends(get_tutor_repository),
) -> TutorServiceProtocol:
    return TutorService(tutor_repo=tutor_repo)
