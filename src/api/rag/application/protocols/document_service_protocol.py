from typing import Protocol, runtime_checkable


@runtime_checkable
class DocumentServiceProtocol(Protocol):
    """Defines the contract for managing the document lifecycle."""

    def delete_document_from_tutor(self, document_id: int, tutor_id: int) -> None: ...
