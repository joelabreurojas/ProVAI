from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.chat.domain.models import Chat
    from src.rag.domain.models import Document


@runtime_checkable
class ChatRepositoryProtocol(Protocol):
    """Defines the contract for the chat data repository."""

    def get_chat_by_id(self, chat_id: int) -> Optional["Chat"]: ...
    def link_document_to_chat(self, chat: "Chat", document: "Document") -> None: ...
    def get_chunk_hashes_for_chat(self, chat_id: int) -> list[str]: ...
    def remove_document_from_chat(self, chat: "Chat", document: "Document") -> None: ...
