import logging

from langchain_chroma import Chroma

from src.assistant.application.exceptions import AssistantNotFoundError
from src.assistant.application.protocols import AssistantRepositoryProtocol
from src.rag.application.exceptions import DocumentNotFoundError
from src.rag.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    DocumentServiceProtocol,
)

logger = logging.getLogger(__name__)


class DocumentService(DocumentServiceProtocol):
    """
    Manages the lifecycle of documents, including deletion and garbage collection.
    """

    def __init__(
        self,
        doc_repo: DocumentRepositoryProtocol,
        chunk_repo: ChunkRepositoryProtocol,
        assistant_repo: AssistantRepositoryProtocol,
        vector_store: Chroma,
    ):
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.assistant_repo = assistant_repo
        self.vector_store = vector_store

    def delete_document_from_assistant(
        self, document_id: int, assistant_id: int
    ) -> None:
        """
        Removes a document's link to an assistant and performs garbage collection
        on any chunks that are no longer referenced by any other documents.
        """
        assistant = self.assistant_repo.get_assistant_by_id(assistant_id)
        if not assistant:
            raise AssistantNotFoundError(assistant_id=assistant_id)

        document = self.doc_repo.get_document_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(document_id=document_id)

        self.assistant_repo.remove_document_from_assistant(assistant, document)

        if not document.assistants:
            logger.info(
                f"Document {document_id} is now orphaned. Starting garbage collection."
            )

            orphaned_chunks = self.chunk_repo.get_orphaned_chunks(document)
            chunk_hashes_to_delete = [c.content_hash for c in orphaned_chunks]

            if orphaned_chunks:
                self.chunk_repo.delete_chunks(orphaned_chunks)

            self.doc_repo.delete_document(document)

            if chunk_hashes_to_delete:
                self.vector_store.delete(ids=chunk_hashes_to_delete)
                logger.info(
                    f"Garbage collected {len(chunk_hashes_to_delete)} orphaned chunks \
                    from vector store."
                )
