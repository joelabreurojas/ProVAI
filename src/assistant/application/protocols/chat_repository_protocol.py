# Renamed from SessionRepositoryProtocol
from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.assistant.domain.models import Chat, Message


@runtime_checkable
class ChatRepositoryProtocol(Protocol):
    """Defines the contract for the chat and message data repository."""

    def create_chat(self, assistant_id: int, user_id: int, title: str) -> "Chat": ...
    def get_chat_by_id(self, chat_id: int) -> Optional["Chat"]: ...
    def get_chats_for_user(self, user_id: int) -> list["Chat"]: ...
    def add_message(self, chat_id: int, role: str, content: str) -> "Message": ...
