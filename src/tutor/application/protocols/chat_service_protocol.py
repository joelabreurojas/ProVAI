from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.tutor.domain.models import Chat, Message


@runtime_checkable
class ChatServiceProtocol(Protocol):
    """Defines the contract for the main chat and message service."""

    def create_new_chat(self, tutor_id: int, user_id: int, title: str) -> "Chat": ...
    def get_chat(self, chat_id: int) -> "Chat": ...
    def get_chats(self, tutor_id: int, user_id: int) -> list["Chat"]: ...
    def log_interaction(
        self, chat_id: int, user_query: str, tutor_response: str
    ) -> None: ...
    def get_history(self, chat_id: int) -> list["Message"]: ...
