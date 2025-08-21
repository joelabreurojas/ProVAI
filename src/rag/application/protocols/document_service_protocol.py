from typing import Protocol, runtime_checkable


@runtime_checkable
class DocumentServiceProtocol(Protocol):
    """Defines the contract for managing the document lifecycle."""

    def delete_document_from_assistant(
        self, document_id: int, assistant_id: int
    ) -> None: ...
