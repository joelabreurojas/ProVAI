from typing import Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from pydantic import BaseModel, EmailStr

from src.api.auth.infrastructure.dependencies import get_current_user
from src.api.rag.infrastructure.dependencies import (
    get_document_service,
    get_ingestion_service,
)
from src.api.tutor.infrastructure.dependencies import get_tutor_service
from src.core.application.protocols import (
    DocumentServiceProtocol,
    IngestionServiceProtocol,
    TutorServiceProtocol,
)
from src.core.domain.models import Tutor, User
from src.core.domain.schemas import (
    TutorCreate,
    TutorResponse,
    TutorResponseWithToken,
    TutorUpdate,
)
from src.core.infrastructure.limiter import limiter
from src.core.infrastructure.settings import settings

TAG = {
    "name": "Tutor",
    "description": "Create, manage, and enroll in AI Tutors.",
}
router = APIRouter(prefix="/tutors", tags=[TAG["name"]])


class EmailsPayload(BaseModel):
    emails: list[EmailStr]


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


@router.get("/{tutor_id}", response_model=TutorResponseWithToken)
async def get_tutor_details(
    tutor_id: int,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> Tutor:
    """
    Retrieves the details of a specific tutor. Only the owner (teacher) can
    access sensitive details like the invitation token.
    """
    tutor = tutor_service.verify_user_is_tutor_owner(
        tutor_id=tutor_id, user=current_user
    )
    return tutor


@router.patch("/{tutor_id}", response_model=TutorResponse)
async def update_tutor_details(
    tutor_id: int,
    tutor_data: TutorUpdate,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> Tutor:
    """
    Update a tutor's details (e.g., course_name, description).
    Only the owner (teacher) of the tutor can perform this action.
    """
    updated_tutor = tutor_service.update_tutor(
        tutor_id=tutor_id, tutor_update=tutor_data, requesting_user=current_user
    )
    return updated_tutor


@router.post(
    "/{tutor_id}/authorized-emails",
    status_code=status.HTTP_200_OK,
    summary="Update the list of students authorized to join a Tutor",
)
async def add_authorized_emails_to_tutor(
    tutor_id: int,
    payload: EmailsPayload,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> dict[str, str]:
    """
    Adds a list of student emails to the invitation whitelist for a specific Tutor.
    This action is idempotent; adding an existing email has no effect.
    Only the owner of the Tutor can perform this action.
    """
    # The router's only job is to call the service.
    # All logic (auth, db writes) is handled inside the service.
    tutor_service.add_authorized_students(
        tutor_id=tutor_id, requesting_user=current_user, student_emails=payload.emails
    )
    return {"message": "Authorized emails updated successfully."}


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

    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)  # Reset the file pointer to the beginning

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the limit of {settings.MAX_UPLOAD_SIZE_MB} MB.",
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


@router.delete(
    "/{tutor_id}/authorized-emails/{student_email}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a student's access to a Tutor",
)
async def remove_student_from_tutor(
    tutor_id: int,
    student_email: EmailStr,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> None:
    """
    Revokes a student's access to a Tutor.

    This action performs two operations:
    1. Removes the student's email from the invitation whitelist.
    2. Unenrolls the student from the Tutor if they were already a member.

    Only the owner (teacher) of the Tutor can perform this action.
    """
    tutor_service.remove_student_access(
        tutor_id=tutor_id,
        student_email=student_email,
        requesting_user=current_user,
    )


@router.delete("/{tutor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tutor(
    tutor_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
    doc_service: DocumentServiceProtocol = Depends(get_document_service),
) -> None:
    """
    Deletes a tutor and schedules background jobs for cascading garbage collection.
    """
    doc_ids_to_check = tutor_service.delete_tutor(
        tutor_id=tutor_id, requesting_user=current_user
    )

    # The response will be sent to the user immediately, and FastAPI will
    # run this loop in the background.
    for doc_id in doc_ids_to_check:
        background_tasks.add_task(doc_service.handle_potential_orphan, doc_id)
