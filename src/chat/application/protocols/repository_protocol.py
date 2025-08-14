from typing import (
    TYPE_CHECKING,
    Optional,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from src.chat.domain.models import Message, Session


@runtime_checkable
class HistoryRepositoryProtocol(Protocol):
    """Defines the contract for the chat history data repository."""

    def create_session(self, chat_id: int, user_id: int) -> "Session": ...

    def add_message(self, session_id: int, role: str, content: str) -> "Message": ...

    def get_session_by_id(self, session_id: int) -> Optional["Session"]: ...
