from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.core.domain.models import Chat, Document, Message, User
    from src.core.domain.schemas import ChatUpdate, MessageUpdate


@runtime_checkable
class ChatRepositoryProtocol(Protocol):
    """Defines the contract for the chat and message data repository."""

    def create_chat(self, tutor_id: int, user_id: int, title: str) -> "Chat": ...

    def get_chat_by_id(self, chat_id: int) -> Optional["Chat"]: ...

    def get_chats_for_user(self, user_id: int) -> list["Chat"]: ...

    def update_chat(self, chat: "Chat", chat_update: "ChatUpdate") -> "Chat": ...

    def delete_chat(self, chat: "Chat") -> None: ...

    def add_message(self, chat_id: int, role: str, content: str) -> "Message": ...

    def get_message_by_id(self, message_id: int) -> Optional["Message"]: ...

    def get_preceding_user_message(
        self, ai_message: "Message"
    ) -> Optional["Message"]: ...

    def update_message(
        self, message: "Message", message_update: "MessageUpdate"
    ) -> "Message": ...

    def delete_message(self, message: "Message") -> None: ...


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

    def update_chat(
        self, chat_id: int, chat_update: "ChatUpdate", requesting_user: "User"
    ) -> "Chat": ...

    def delete_chat(self, chat_id: int, requesting_user: "User") -> None: ...

    def post_message(self, chat_id: int, query: str, current_user: "User") -> str: ...

    def log_interaction(
        self,
        chat_id: int,
        role: str,
        user_query: str | None = None,
        tutor_response: str | None = None,
    ) -> None: ...

    def get_history(self, chat_id: int, user: "User") -> list["Message"]: ...

    def regenerate_response(
        self, message_id: int, requesting_user: "User"
    ) -> "Message": ...

    def update_user_message(
        self, message_id: int, message_update: "MessageUpdate", requesting_user: "User"
    ) -> "Message": ...

    def delete_message(self, message_id: int, requesting_user: "User") -> None: ...
