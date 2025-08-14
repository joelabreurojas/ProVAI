from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.chat.domain.models import Message, Session  # Use new models


@runtime_checkable
class HistoryServiceProtocol(Protocol):
    def get_or_create_session(self, chat_id: int, user_id: int) -> "Session": ...
    def log_interaction(
        self, session_id: int, user_query: str, assistant_response: str
    ) -> None: ...
    def get_history(self, session_id: int) -> list["Message"]: ...
