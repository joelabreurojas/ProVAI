from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

# This block is only executed by the static type checker (mypy).
# It is completely ignored at runtime, preventing circular dependencies
# and keeping our architectural layers pure.
if TYPE_CHECKING:
    from src.domain.models import Document, SessionHistory, User
    from src.domain.schemas import UserCreate  # We will create this schema later


@runtime_checkable
class AuthServiceProtocol(Protocol):
    """Defines the contract for authentication services."""

    # We use forward-references (strings) for the types.
    # mypy understands this because of the TYPE_CHECKING block above.
    def register_user(self, user_create: "UserCreate") -> "User":
        """Registers a new user and returns the domain model instance."""
        ...

    def authenticate_user(self, email: str, password: str) -> "User":
        """Authenticates a user and returns the domain model if valid."""
        ...

    def create_access_token(self, data: dict[str, Any]) -> str:
        """Creates a JWT access token."""
        ...


@runtime_checkable
class IngestionServiceProtocol(Protocol):
    """Defines the contract for document ingestion services."""

    def ingest_document(
        self, file_bytes: bytes, file_name: str, chat_id: int
    ) -> "Document":
        """Processes a document and returns the created domain model instance."""
        ...


@runtime_checkable
class HistoryServiceProtocol(Protocol):
    """Defines the contract for managing chat history."""

    def log_interaction(
        self, *, chat_id: int, user_query: str, ai_response: str
    ) -> "SessionHistory":
        """Logs an interaction and returns the created history record."""
        ...

    def get_history(self, *, chat_id: int) -> Sequence["SessionHistory"]:
        """Retrieves the full conversation history for a specific chat."""
        ...


@runtime_checkable
class RAGServiceProtocol(Protocol):
    """Defines the contract for the core RAG query engine."""

    def answer_query(self, *, query: str, chat_id: int) -> str:
        """Takes a user query and a chat context, and returns a generated answer."""
        ...
