import logging

from langsmith import traceable

from src.core.application.exceptions import (
    InsufficientPermissionsError,
    InvitationEmailMismatchError,
    InvitationNotFoundError,
    SelfEnrollmentError,
    TutorNotFoundError,
    TutorOwnershipError,
    UserAlreadyEnrolledError,
    UserNotEnrolledError,
)
from src.core.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.core.domain.models import Document, Tutor, User
from src.core.domain.schemas import TutorCreate, TutorUpdate

logger = logging.getLogger(__name__)


class TutorService(TutorServiceProtocol):
    """
    The main application service for handling all high-level business logic
    related to Tutors, including creation, authorization, and student management.
    """

    def __init__(self, tutor_repo: TutorRepositoryProtocol):
        self.tutor_repo = tutor_repo

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

    def get_tutors_for_user(self, user: User) -> list[Tutor]:
        """Pass-through method to get all tutors for a given user."""
        return self.tutor_repo.get_tutors_for_user(user)

    @traceable(name="Update Tutor")
    def update_tutor(
        self, tutor_id: int, tutor_update: TutorUpdate, requesting_user: User
    ) -> Tutor:
        """
        Updates a tutor's details after verifying the requesting user is the owner.
        """
        tutor = self.verify_user_is_tutor_owner(tutor_id, requesting_user)

        return self.tutor_repo.update_tutor(tutor, tutor_update)

    @traceable(name="Add Authorized Students")
    def add_authorized_students(
        self, tutor_id: int, requesting_user: User, student_emails: list[str]
    ) -> None:
        """
        Authorizes the requesting user and adds a list of student emails to
        the tutor's invitation whitelist.
        """
        tutor = self.verify_user_is_tutor_owner(tutor_id, requesting_user)

        self.tutor_repo.add_authorized_emails(tutor, student_emails)

        logger.info(
            f"Updated authorized emails for Tutor {tutor_id} "
            f"by Teacher {requesting_user.id}."
        )

    @traceable(name="Enroll Student")
    def enroll_student_from_token(self, token: str, student_user: User) -> Tutor:
        """
        Enrolls a student by consuming a valid tutor token.
        """
        tutor = self.tutor_repo.get_tutor_by_token(token)

        if not tutor:
            raise InvitationNotFoundError()

        authorized_emails = self.tutor_repo.get_authorized_emails(tutor)
        if student_user.email not in authorized_emails:
            raise InvitationEmailMismatchError()

        # ... rest of the logic remains the same ...
        if any(s.id == student_user.id for s in tutor.students):
            raise UserAlreadyEnrolledError()

        if tutor.teacher_id == student_user.id:
            raise SelfEnrollmentError()

        self.tutor_repo.add_student_to_tutor(tutor, student_user)
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

    @traceable(name="Delete Tutor")
    def delete_tutor(self, tutor_id: int, requesting_user: User) -> list[int]:
        tutor = self.verify_user_is_tutor_owner(tutor_id, requesting_user)

        doc_ids_to_check = [doc.id for doc in tutor.documents]

        self.tutor_repo.delete_tutor(tutor)
        logger.info(f"Deleted Tutor {tutor_id} by Teacher {requesting_user.id}.")

        return doc_ids_to_check
