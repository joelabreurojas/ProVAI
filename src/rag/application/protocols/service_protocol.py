from typing import Protocol, runtime_checkable


@runtime_checkable
class IngestionServiceProtocol(Protocol):
    """Defines the contract for the document ingestion service."""

    def ingest_document(
        self, file_bytes: bytes, file_name: str, chat_id: int
    ) -> None: ...


@runtime_checkable
class RAGServiceProtocol(Protocol):
    """Defines the contract for the main RAG orchestration service."""

    def answer_query(self, query: str, chat_id: int) -> str: ...
