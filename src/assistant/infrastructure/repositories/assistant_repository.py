from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import joinedload

from src.assistant.application.protocols import AssistantRepositoryProtocol
from src.assistant.domain.models import Assistant
from src.rag.domain.models import Document


class SQLAlchemyAssistantRepository(AssistantRepositoryProtocol):
    """
    Concrete implementation of the Assistant repository using SQLAlchemy.
    """

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def get_assistant_by_id(self, assistant_id: int) -> Assistant | None:
        return self.db.query(Assistant).filter(Assistant.id == assistant_id).first()

    def link_document_to_assistant(
        self, assistant: Assistant, document: Document
    ) -> None:
        if document not in assistant.documents:
            assistant.documents.append(document)
            self.db.commit()

    def remove_document_from_assistant(
        self, assistant: Assistant, document: Document
    ) -> None:
        if document in assistant.documents:
            assistant.documents.remove(document)
            self.db.commit()

    def get_chunk_hashes_for_assistant(self, assistant_id: int) -> list[str]:
        """
        Performs an efficient query to get all unique content_hashes for
        all chunks related to a specific assistant.
        """
        assistant = (
            self.db.query(Assistant)
            .options(joinedload(Assistant.documents).joinedload(Document.chunks))
            .filter(Assistant.id == assistant_id)
            .first()
        )

        if not assistant:
            return []

        # Use a set to efficiently find unique chunk hashes
        unique_chunk_hashes = {
            chunk.content_hash
            for document in assistant.documents
            for chunk in document.chunks
        }

        return list(unique_chunk_hashes)
