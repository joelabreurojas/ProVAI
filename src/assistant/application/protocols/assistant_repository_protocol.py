from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.assistant.domain.models import Assistant
    from src.rag.domain.models import Document


@runtime_checkable
class AssistantRepositoryProtocol(Protocol):
    """Defines the contract for the assistant data repository."""

    def get_assistant_by_id(self, assistant_id: int) -> Optional["Assistant"]: ...
    def link_document_to_assistant(
        self, assistant: "Assistant", document: "Document"
    ) -> None: ...
    def get_chunk_hashes_for_assistant(self, assistant_id: int) -> list[str]: ...
    def remove_document_from_assistant(
        self, assistant: "Assistant", document: "Document"
    ) -> None: ...
