from typing import Protocol, runtime_checkable

from src.api.rag.domain.models import Document


@runtime_checkable
class IngestionServiceProtocol(Protocol):
    """Defines the contract for the document ingestion service."""

    def ingest_document(self, file_bytes: bytes, file_name: str) -> Document: ...
