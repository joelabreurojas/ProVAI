from datetime import timedelta

from src.auth.application.exceptions import (
    InsufficientPermissionsError,
    TokenInvalidScopeError,
    TokenMissingDataError,
    TokenValidationError,
)
from src.auth.application.protocols import TokenServiceProtocol
from src.auth.domain.models import User
from src.rag.domain.models import Document
from src.tutor.application.exceptions import (
    InvitationEmailMismatchError,
    SelfEnrollmentError,
    TutorNotFoundError,
    TutorOwnershipError,
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)
from src.tutor.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.tutor.domain.models import Tutor
from src.tutor.domain.schemas import TutorCreate, TutorInvitationResponse


class TutorService(TutorServiceProtocol):
    """
    The main application service for handling all high-level business logic
    related to Tutors, including creation, authorization, and student management.
    """

    def __init__(
        self,
        tutor_repo: TutorRepositoryProtocol,
        token_service: TokenServiceProtocol,
    ):
        self.tutor_repo = tutor_repo
        self.token_service = token_service

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

    def link_document_to_tutor(self, tutor: Tutor, document: Document) -> None:
        """Links an existing Document object to a Tutor."""
        self.tutor_repo.link_document_to_tutor(tutor, document)

    def create_invitations(
        self, tutor_id: int, requesting_user: User, student_emails: list[str]
    ) -> list[TutorInvitationResponse]:
        """
        Authorizes the teacher and creates invitation tokens for a list of emails,
        returning a detailed status for each.
        """
        self.verify_user_is_tutor_owner(tutor_id, requesting_user)

        responses = []
        for email in set(student_emails):  # De-duplicate emails
            expires_delta = timedelta(days=7)
            token_data = {
                "tutor_id": tutor_id,
                "scope": "enrollment",
                "student_email": email,
            }
            token = self.token_service.create_access_token(
                data=token_data, expires_delta=expires_delta
            )
            responses.append(
                TutorInvitationResponse(
                    email=email, status="invitation_created_successfully", token=token
                )
            )
        return responses

    def enroll_student(self, token: str, student_user: User) -> None:
        """Enrolls a student in a tutor using a valid invitation token."""
        payload = self.token_service.decode_access_token(token)

        if payload is None:
            raise TokenValidationError()

        if payload.get("scope") != "enrollment":
            raise TokenInvalidScopeError()

        tutor_id = payload.get("tutor_id")
        authorized_email = payload.get("student_email")

        if not tutor_id or not authorized_email:
            raise TokenMissingDataError()

        if authorized_email != student_user.email:
            raise InvitationEmailMismatchError()

        tutor = self.get_tutor(tutor_id)

        if tutor.teacher_id == student_user.id:
            raise SelfEnrollmentError()

        if any(s.id == student_user.id for s in tutor.students):
            raise UserAlreadyEnrolledError()

        self.tutor_repo.add_student_to_tutor(tutor, student_user)

    def verify_user_is_tutor_owner(self, tutor_id: int, user: User) -> Tutor:
        """Verifies ownership and returns the tutor object if successful."""
        if user.role != "teacher":
            raise InsufficientPermissionsError()

        tutor = self.get_tutor(tutor_id)
        if tutor.teacher_id != user.id:
            raise TutorOwnershipError()

        return tutor

    def verify_user_can_access_tutor(self, tutor_id: int, user: User) -> Tutor:
        """Verifies access and returns the tutor object if successful."""
        tutor = self.get_tutor(tutor_id)
        is_teacher = tutor.teacher_id == user.id
        is_student = any(s.id == user.id for s in tutor.students)

        if not is_teacher and not is_student:
            raise UserNotEnrolledError()

        return tutor
