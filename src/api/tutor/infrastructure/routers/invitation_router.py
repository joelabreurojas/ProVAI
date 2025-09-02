from fastapi import APIRouter, Depends, status

from src.api.auth.dependencies import get_current_user
from src.api.auth.domain.models import User
from src.api.tutor.application.protocols import TutorServiceProtocol
from src.api.tutor.dependencies import get_tutor_service
from src.api.tutor.domain.schemas import (
    TutorInvitationCreate,
    TutorInvitationResponse,
)

TAG = {
    "name": "Invitations",
    "description": "Create and manage invitations for students to join a Tutor.",
}
router = APIRouter(prefix="/invitations", tags=[TAG["name"]])


@router.post(
    "", response_model=TutorInvitationResponse, status_code=status.HTTP_201_CREATED
)
async def create_invitation(
    invitation_data: TutorInvitationCreate,
    current_user: User = Depends(get_current_user),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> TutorInvitationResponse:
    """
    Creates a single, shareable invitation link for a group of students to
    join a specific Tutor.
    """
    return tutor_service.add_students_to_invitation(
        tutor_id=invitation_data.tutor_id,
        requesting_user=current_user,
        student_emails=invitation_data.student_emails,
    )
