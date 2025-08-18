from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.chat.domain.models import Message, Session


@runtime_checkable
class SessionRepositoryProtocol(Protocol):
    """Defines the contract for the session and message data repository."""

    def create_session(self, chat_id: int, user_id: int) -> "Session": ...
    def get_session_by_id(self, session_id: int) -> Optional["Session"]: ...
    def get_latest_session(self, chat_id: int, user_id: int) -> Optional["Session"]: ...
    def add_message(self, session_id: int, role: str, content: str) -> "Message": ...
