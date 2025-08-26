import logging

from langsmith import traceable

from src.auth.application.exceptions import InsufficientPermissionsError
from src.auth.domain.models import User
from src.rag.domain.models import Document
from src.tutor.application.exceptions import (
    InvitationEmailMismatchError,
    InvitationNotFoundError,
    SelfEnrollmentError,
    TutorNotFoundError,
    TutorOwnershipError,
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)
from src.tutor.application.protocols import (
    InvitationRepositoryProtocol,
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.tutor.domain.models import Invitation, Tutor
from src.tutor.domain.schemas import TutorCreate, TutorInvitationResponse

logger = logging.getLogger(__name__)


class TutorService(TutorServiceProtocol):
    """
    The main application service for handling all high-level business logic
    related to Tutors, including creation, authorization, and student management.
    """

    def __init__(
        self,
        tutor_repo: TutorRepositoryProtocol,
        invitation_repo: InvitationRepositoryProtocol,
    ):
        self.tutor_repo = tutor_repo
        self.invitation_repo = invitation_repo

    @traceable(name="Create Tutor")
    def create_tutor(self, tutor_create: TutorCreate, teacher: User) -> Tutor:
        """Creates a new Tutor, enforcing that only teachers can create them."""
        if teacher.role != "teacher":
            raise InsufficientPermissionsError()
        return self.tutor_repo.create_tutor(
            tutor_create=tutor_create, teacher_id=teacher.id
        )

    def get_tutor(self, tutor_id: int) -> Tutor:
        """Retrieves a single tutor by its ID, raising an error if not found."""
        tutor = self.tutor_repo.get_tutor_by_id(tutor_id)
        if not tutor:
            raise TutorNotFoundError(tutor_id=tutor_id)
        return tutor

    @traceable(name="Get or Create Invitation")
    def get_or_create_invitation(
        self, tutor_id: int, requesting_user: User
    ) -> Invitation:
        """
        Gets the single, living invitation for a tutor, or creates it if it
        doesn't exist. This is a teacher-only action.
        """
        tutor = self.verify_user_is_tutor_owner(tutor_id, requesting_user)
        invitation = self.invitation_repo.get_by_tutor_id(tutor.id)
        if not invitation:
            invitation = self.invitation_repo.create_for_tutor(tutor.id)
        return invitation

    @traceable(name="Add Students to Invitation")
    def add_students_to_invitation(
        self, tutor_id: int, requesting_user: User, student_emails: list[str]
    ) -> TutorInvitationResponse:
        """
        Adds a list of students to a tutor's permanent invitation list and
        returns the single, shareable invitation.
        """
        invitation = self.get_or_create_invitation(tutor_id, requesting_user)
        self.invitation_repo.add_members(invitation, student_emails)

        return TutorInvitationResponse(
            tutor_id=invitation.tutor_id,
            invitation_token=invitation.token,
            status=f"Added/Updated invitation for {len(set(student_emails))} students.",
        )

    @traceable(name="Enroll Student")
    def enroll_student_from_token(self, token: str, student_user: User) -> Tutor:
        """
        Enrolls a student by consuming a valid invitation token, implementing
        all necessary security checks with specific error handling.
        """
        invitation = self.invitation_repo.get_by_token(token)
        if not invitation:
            raise InvitationNotFoundError()

        authorized_member = next(
            (m for m in invitation.members if m.student_email == student_user.email),
            None,
        )
        if not authorized_member:
            raise InvitationEmailMismatchError()

        if authorized_member.status == "accepted":
            raise UserAlreadyEnrolledError()

        tutor = self.get_tutor(invitation.tutor_id)

        if any(s.id == student_user.id for s in tutor.students):
            raise UserAlreadyEnrolledError()

        if tutor.teacher_id == student_user.id:
            raise SelfEnrollmentError()

        self.tutor_repo.add_student_to_tutor(tutor, student_user)
        self.invitation_repo.update_member_status(
            invitation, student_user.email, "accepted"
        )

        logger.info(f"Student {student_user.id} enrolled in Tutor {tutor.id}")

        return tutor

    def link_document_to_tutor(self, tutor: Tutor, document: Document) -> None:
        """Links an existing Document object to a Tutor."""
        self.tutor_repo.link_document_to_tutor(tutor, document)

    def verify_user_is_tutor_owner(self, tutor_id: int, user: User) -> Tutor:
        """Verifies ownership and returns the tutor object if successful."""
        if user.role != "teacher":
            raise InsufficientPermissionsError()
        tutor = self.get_tutor(tutor_id)
        if tutor.teacher_id != user.id:
            raise TutorOwnershipError()
        return tutor

    def verify_user_can_access_tutor(self, tutor_id: int, user: User) -> Tutor:
        """
        Verifies a user can access a tutor, either as its teacher or as an
        enrolled student. Raises UserNotEnrolledError if not authorized.
        """
        tutor = self.get_tutor(tutor_id)
        is_teacher = tutor.teacher_id == user.id
        is_student = any(s.id == user.id for s in tutor.students)

        if not is_teacher and not is_student:
            raise UserNotEnrolledError()
        return tutor
