from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.chat.domain.models import SessionHistory


@runtime_checkable
class HistoryRepositoryProtocol(Protocol):
    """Defines the contract for the chat history data repository."""

    def add_interaction(
        self, chat_id: int, user_id: int, query: str, response: str
    ) -> "SessionHistory": ...

    def get_history_by_chat_id(self, chat_id: int) -> list["SessionHistory"]: ...
