from typing import Protocol, runtime_checkable


@runtime_checkable
class RAGServiceProtocol(Protocol):
    """Defines the contract for the main RAG orchestration service."""

    def answer_query(self, query: str, tutor_id: int) -> str: ...
