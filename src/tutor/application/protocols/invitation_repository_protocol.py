from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.tutor.domain.models import Invitation


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
