from typing import Any

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from src.api.auth.domain.models import User
from src.api.auth.infrastructure.dependencies import get_current_user
from src.api.rag.application.protocols import IngestionServiceProtocol
from src.api.rag.infrastructure.dependencies import get_ingestion_service
from src.api.tutor.application.protocols import TutorServiceProtocol
from src.api.tutor.domain.schemas import (
    TutorCreate,
    TutorResponse,
)
from src.api.tutor.infrastructure.dependencies import get_tutor_service
from src.core.infrastructure.limiter import limiter

TAG = {
    "name": "Tutor",
    "description": "Create, manage, and enroll in AI Tutors.",
}
router = APIRouter(prefix="/tutors", tags=[TAG["name"]])


@router.get("", response_model=list[TutorResponse])
async def get_my_tutors(
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> list[TutorResponse]:
    """Retrieves a list of all Tutors associated with the current user."""
    tutors = tutor_service.get_tutors_for_user(current_user)
    return [TutorResponse.model_validate(tutor) for tutor in tutors]


@router.post(
    "",
    response_model=TutorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tutor",
)
async def create_tutor(
    tutor_data: TutorCreate,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> TutorResponse:
    """Creates a new tutor for the current user."""
    new_tutor = tutor_service.create_tutor(
        tutor_create=tutor_data, teacher=current_user
    )
    return TutorResponse.model_validate(new_tutor)


@router.post(
    "/{tutor_id}/documents",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document to the tutor's knowledge base",
)
@limiter.limit("5/minute")
async def upload_document_to_tutor(
    request: Request,
    tutor_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
    ingestion_service: IngestionServiceProtocol = Depends(get_ingestion_service),
) -> dict[str, Any]:
    """Uploads a document to the tutor's knowledge base."""
    tutor = tutor_service.verify_user_is_tutor_owner(
        tutor_id=tutor_id, user=current_user
    )

    file_bytes = await file.read()
    new_document = ingestion_service.ingest_document(
        file_bytes=file_bytes,
        file_name=file.filename or "unknown.pdf",
    )

    tutor_service.link_document_to_tutor(tutor, new_document)

    message = (
        f"Successfully added '{new_document.file_name}' to Tutor '{tutor.course_name}'."
    )
    return {
        "message": message,
        "document_id": new_document.id,
    }
