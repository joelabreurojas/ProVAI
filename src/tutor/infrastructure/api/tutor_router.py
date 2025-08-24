from fastapi import APIRouter, Depends, File, UploadFile, status

from src.auth.dependencies import get_current_user
from src.auth.domain.models import User
from src.rag.application.protocols import (
    IngestionServiceProtocol,
    RAGServiceProtocol,
)
from src.rag.dependencies import get_ingestion_service, get_rag_service
from src.tutor.application.protocols import TutorServiceProtocol
from src.tutor.dependencies import get_tutor_service
from src.tutor.domain.schemas import (
    StudentEnrollmentCreate,
    TutorCreate,
    TutorInvitationCreate,
    TutorInvitationResponse,
    TutorResponse,
)

TAG = {
    "name": "Tutor",
    "description": "Create, manage, and interact with AI Tutors.",
}
router = APIRouter(prefix="/tutors", tags=[TAG["name"]])


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
    new_tutor = tutor_service.create_tutor(
        tutor_create=tutor_data, teacher=current_user
    )
    return TutorResponse.model_validate(new_tutor)


@router.post(
    "/{tutor_id}/invitations",
    response_model=list[TutorInvitationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Invite students to a tutor",
)
async def invite_students(
    tutor_id: int,
    invitation_data: TutorInvitationCreate,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> list[TutorInvitationResponse]:
    return tutor_service.create_invitations(
        tutor_id=tutor_id,
        requesting_user=current_user,
        student_emails=invitation_data.student_emails,
    )


@router.post(
    "/{tutor_id}/enrollments",
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in a tutor",
)
async def enroll_student(
    tutor_id: int,
    enrollment_data: StudentEnrollmentCreate,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> dict[str, str]:
    tutor_service.enroll_student(
        token=enrollment_data.invitation_token, student_user=current_user
    )
    return {"message": "Successfully enrolled in the tutor."}


@router.post(
    "/{tutor_id}/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document to a tutor",
)
async def upload_document_to_tutor(
    tutor_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
    ingestion_service: IngestionServiceProtocol = Depends(get_ingestion_service),
) -> dict[str, str]:
    tutor_service.verify_user_is_tutor_owner(tutor_id=tutor_id, user=current_user)
    file_bytes = await file.read()
    ingestion_service.ingest_document(
        file_bytes=file_bytes,
        file_name=file.filename or "unknown.pdf",
        tutor_id=tutor_id,
    )
    return {"message": f"Successfully ingested '{file.filename}'."}


@router.post("/{tutor_id}/query", summary="Query a tutor")
async def query_tutor(
    tutor_id: int,
    query: str,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
    rag_service: RAGServiceProtocol = Depends(get_rag_service),
) -> dict[str, str]:
    tutor_service.verify_user_can_access_tutor(tutor_id=tutor_id, user=current_user)
    answer = rag_service.answer_query(query=query, tutor_id=tutor_id)
    return {"answer": answer}
