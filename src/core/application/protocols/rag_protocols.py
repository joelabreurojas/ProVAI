from typing import TYPE_CHECKING, Any, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.core.domain.models import Chunk, Document


@runtime_checkable
class ChunkRepositoryProtocol(Protocol):
    """Defines the contract for the chunk data repository."""

    def create_chunk(self, content_hash: str) -> "Chunk": ...

    def get_chunk_by_hash(self, content_hash: str) -> Optional["Chunk"]: ...

    def get_existing_chunks_by_hashes(self, content_hashes: list[str]) -> set[str]: ...

    def get_many_chunks_by_document(self, document: "Document") -> list["Chunk"]: ...

    def get_orphaned_chunks(self, document: "Document") -> list["Chunk"]: ...

    def delete_chunks(self, chunks: list["Chunk"]) -> None: ...


@runtime_checkable
class DocumentRepositoryProtocol(Protocol):
    """Defines the contract for the document data repository."""

    def create_document(self, file_name: str, storage_path: str) -> "Document": ...

    def get_document_by_id(self, document_id: int) -> Optional["Document"]: ...

    def link_chunk_to_document(
        self, db_document: "Document", db_chunk: "Chunk"
    ) -> None: ...

    def delete_document(self, document: "Document") -> None: ...


@runtime_checkable
class DocumentServiceProtocol(Protocol):
    """Defines the contract for managing the document lifecycle."""

    def delete_document_from_tutor(self, document_id: int, tutor_id: int) -> None: ...

    def handle_potential_orphan(self, document_id: int) -> None: ...


@runtime_checkable
class IngestionServiceProtocol(Protocol):
    """Defines the contract for the document ingestion service."""

    def ingest_document(self, file_bytes: bytes, file_name: str) -> "Document": ...


@runtime_checkable
class RAGServiceProtocol(Protocol):
    """Defines the contract for the main RAG orchestration service."""

    def answer_query(self, query: str, context_filter: dict[str, Any]) -> str: ...
