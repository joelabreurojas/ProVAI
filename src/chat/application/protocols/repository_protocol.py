from typing import (
    TYPE_CHECKING,
    Optional,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from src.chat.domain.models import Chunk, Document, Message, Session


@runtime_checkable
class HistoryRepositoryProtocol(Protocol):
    """Defines the contract for the chat history data repository."""

    def create_session(self, chat_id: int, user_id: int) -> "Session": ...
    def add_message(self, session_id: int, role: str, content: str) -> "Message": ...
    def get_session_by_id(self, session_id: int) -> Optional["Session"]: ...


@runtime_checkable
class ContentRepositoryProtocol(Protocol):
    """Defines the contract for the content management repository."""

    def create_document(self, file_name: str, chat_id: int) -> "Document": ...
    def get_chunk_by_hash(self, content_hash: str) -> Optional["Chunk"]: ...
    def create_chunk(self, content_hash: str) -> "Chunk": ...
    def link_chunk_to_document(
        self, db_document: "Document", db_chunk: "Chunk"
    ) -> None: ...
