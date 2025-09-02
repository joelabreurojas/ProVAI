from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RAGServiceProtocol(Protocol):
    """Defines the contract for the main RAG orchestration service."""

    def answer_query(self, query: str, context_filter: dict[str, Any]) -> str: ...
