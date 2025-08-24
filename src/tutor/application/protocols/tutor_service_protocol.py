from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.document.domain.models import Document
    from src.tutor.domain.models import Tutor
    from src.tutor.domain.schemas import TutorCreate, TutorInvitationResponse


@runtime_checkable
class TutorServiceProtocol(Protocol):
    """
    Defines the contract for the main Tutor service, which handles all
    high-level business logic for creation, authorization, and student management.
    """

    def create_tutor(self, tutor_create: "TutorCreate", teacher: "User") -> "Tutor": ...

    def get_tutor(self, tutor_id: int) -> "Tutor": ...

    def link_document_to_tutor(self, tutor: "Tutor", document: "Document") -> None: ...

    def create_invitations(
        self, tutor_id: int, requesting_user: "User", student_emails: list[str]
    ) -> list["TutorInvitationResponse"]: ...

    def enroll_student(self, token: str, student_user: "User") -> None: ...

    def verify_user_is_tutor_owner(self, tutor_id: int, user: "User") -> "Tutor": ...

    def verify_user_can_access_tutor(self, tutor_id: int, user: "User") -> "Tutor": ...
