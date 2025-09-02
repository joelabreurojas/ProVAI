from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.api.rag.domain.models import Chunk, Document


@runtime_checkable
class DocumentRepositoryProtocol(Protocol):
    """Defines the contract for the document data repository."""

    def create_document(self, file_name: str) -> "Document": ...
    def get_document_by_id(self, document_id: int) -> Optional["Document"]: ...
    def link_chunk_to_document(
        self, db_document: "Document", db_chunk: "Chunk"
    ) -> None: ...
    def delete_document(self, document: "Document") -> None: ...
