from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.api.auth.domain.models import User
    from src.api.chat.domain.models import Chat, Message
    from src.api.rag.domain.models import Document


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
