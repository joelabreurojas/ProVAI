from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.api.auth.domain.models import User
    from src.api.rag.domain.models import Document
    from src.api.tutor.domain.models import Tutor
    from src.api.tutor.domain.schemas import TutorCreate


@runtime_checkable
class TutorRepositoryProtocol(Protocol):
    """
    Defines the contract for the Tutor data repository. This is the sole
    interface for all database operations related to the Tutor entity.
    """

    def create_tutor(self, tutor_create: "TutorCreate", teacher_id: int) -> "Tutor": ...

    def get_tutor_by_id(self, tutor_id: int) -> Optional["Tutor"]: ...

    def add_student_to_tutor(self, tutor: "Tutor", student: "User") -> None: ...

    def link_document_to_tutor(self, tutor: "Tutor", document: "Document") -> None: ...

    def remove_document_from_tutor(
        self, tutor: "Tutor", document: "Document"
    ) -> None: ...

    def get_chunk_hashes_for_tutor(self, tutor_id: int) -> list[str]: ...
