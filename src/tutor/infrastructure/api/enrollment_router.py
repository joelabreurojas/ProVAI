from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.auth.domain.models import User
from src.tutor.application.protocols import TutorServiceProtocol
from src.tutor.dependencies import get_tutor_service
from src.tutor.domain.schemas import StudentEnrollmentCreate, StudentEnrollmentResponse

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
