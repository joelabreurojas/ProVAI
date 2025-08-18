from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.chat.domain.models import Message, Session


@runtime_checkable
class SessionServiceProtocol(Protocol):
    """Defines the contract for the main session and message service."""

    def get_or_create_session(self, chat_id: int, user_id: int) -> "Session": ...
    def log_interaction(
        self, session_id: int, user_query: str, assistant_response: str
    ) -> None: ...
    def get_history(self, session_id: int) -> list["Message"]: ...
