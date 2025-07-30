from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.chat.domain.models import SessionHistory


@runtime_checkable
class HistoryServiceProtocol(Protocol):
    """Defines the contract for the main chat history service."""

    def log_interaction(
        self, chat_id: int, user_id: int, query: str, response: str
    ) -> None: ...

    def get_history(self, chat_id: int) -> list["SessionHistory"]: ...
