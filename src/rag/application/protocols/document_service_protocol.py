from typing import Protocol, runtime_checkable


@runtime_checkable
class DocumentServiceProtocol(Protocol):
    """Defines the contract for managing the document lifecycle."""

    def delete_document_from_chat(self, document_id: int, chat_id: int) -> None: ...
