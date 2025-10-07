from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth.infrastructure.dependencies import get_current_user
from src.api.tutor.infrastructure.dependencies import get_tutor_service
from src.core.application.protocols import TutorServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import (
    StudentEnrollmentCreate,
    StudentEnrollmentResponse,
)

TAG = {
    "name": "Enrollments",
    "description": "Allows students to enroll in a Tutor using an invitation.",
}
router = APIRouter(prefix="/enrollments", tags=[TAG["name"]])


@router.post(
    "", response_model=StudentEnrollmentResponse, status_code=status.HTTP_201_CREATED
)
async def enroll_student(
    enrollment_data: StudentEnrollmentCreate,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> StudentEnrollmentResponse:
    """
    Enrolls the current student in a Tutor by consuming a valid
    invitation token.
    """
    tutor = tutor_service.enroll_student_from_token(
        token=enrollment_data.invitation_token, student_user=current_user
    )
    return StudentEnrollmentResponse(
        tutor_id=tutor.id, user_id=current_user.id, role="student"
    )


@router.delete(
    "/tutors/{tutor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unenroll the current user from a Tutor",
)
async def unenroll_from_tutor(
    tutor_id: int,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> None:
    """
    Unenrolls the currently authenticated user from a specific Tutor.
    """
    tutor_service.unenroll_student(
        tutor_id=tutor_id,
        student_to_unenroll=current_user,
        requesting_user=current_user,
    )
