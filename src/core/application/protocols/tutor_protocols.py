from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.core.domain.models import Document, Invitation, Tutor, User
    from src.core.domain.schemas import TutorCreate, TutorInvitationResponse


@runtime_checkable
class InvitationRepositoryProtocol(Protocol):
    """
    Defines the contract for the Invitation data repository. This is the sole
    interface for all database operations related to the Invitation entity.
    """

    def get_by_tutor_id(self, tutor_id: int) -> Optional["Invitation"]: ...

    def get_by_token(self, token: str) -> Optional["Invitation"]: ...

    def create_for_tutor(self, tutor_id: int) -> "Invitation": ...

    def add_members(
        self, invitation: "Invitation", student_emails: list[str]
    ) -> None: ...

    def update_member_status(
        self, invitation: "Invitation", student_email: str, status: str
    ) -> None: ...


@runtime_checkable
class TutorRepositoryProtocol(Protocol):
    """
    Defines the contract for the Tutor data repository. This is the sole
    interface for all database operations related to the Tutor entity.
    """

    def create_tutor(self, tutor_create: "TutorCreate", teacher_id: int) -> "Tutor": ...

    def get_tutor_by_id(self, tutor_id: int) -> Optional["Tutor"]: ...

    def get_tutors_for_user(self, user: "User") -> list["Tutor"]: ...

    def add_student_to_tutor(self, tutor: "Tutor", student: "User") -> None: ...

    def link_document_to_tutor(self, tutor: "Tutor", document: "Document") -> None: ...

    def remove_document_from_tutor(
        self, tutor: "Tutor", document: "Document"
    ) -> None: ...

    def get_chunk_hashes_for_tutor(self, tutor_id: int) -> list[str]: ...


@runtime_checkable
class TutorServiceProtocol(Protocol):
    """
    Defines the contract for the main Tutor service.
    """

    def create_tutor(self, tutor_create: "TutorCreate", teacher: "User") -> "Tutor": ...

    def get_tutor(self, tutor_id: int) -> "Tutor": ...

    def get_tutors_for_user(self, user: "User") -> list["Tutor"]: ...

    def get_or_create_invitation(
        self, tutor_id: int, requesting_user: "User"
    ) -> "Invitation": ...

    def add_students_to_invitation(
        self, tutor_id: int, requesting_user: "User", student_emails: list[str]
    ) -> "TutorInvitationResponse": ...

    def enroll_student_from_token(
        self, token: str, student_user: "User"
    ) -> "Tutor": ...

    def link_document_to_tutor(self, tutor: "Tutor", document: "Document") -> None: ...

    def verify_user_is_tutor_owner(self, tutor_id: int, user: "User") -> "Tutor": ...

    def verify_user_can_access_tutor(self, tutor_id: int, user: "User") -> "Tutor": ...
