from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.core.domain.models import Chat, Document, Message, User


@runtime_checkable
class ChatRepositoryProtocol(Protocol):
    """Defines the contract for the chat and message data repository."""

    def create_chat(self, tutor_id: int, user_id: int, title: str) -> "Chat": ...

    def get_chat_by_id(self, chat_id: int) -> Optional["Chat"]: ...

    def get_chats_for_user(self, user_id: int) -> list["Chat"]: ...

    def add_message(self, chat_id: int, role: str, content: str) -> "Message": ...


@runtime_checkable
class ChatServiceProtocol(Protocol):
    """Defines the contract for the main Chat orchestrator service."""

    def create_new_chat(self, tutor_id: int, user: "User", title: str) -> "Chat": ...

    def get_chat(self, chat_id: int, user: "User") -> "Chat": ...

    def get_chats_for_user_and_tutor(
        self, tutor_id: int, user: "User"
    ) -> list["Chat"]: ...

    def add_document_to_chat(
        self, chat_id: int, file_bytes: bytes, file_name: str, current_user: "User"
    ) -> "Document": ...

    def post_message(self, chat_id: int, query: str, current_user: "User") -> str: ...

    def log_interaction(
        self,
        chat_id: int,
        role: str,
        user_query: str | None = None,
        tutor_response: str | None = None,
    ) -> None: ...

    def get_history(self, chat_id: int, user: "User") -> list["Message"]: ...
