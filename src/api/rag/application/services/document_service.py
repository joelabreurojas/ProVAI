import logging
import os

from langchain_chroma import Chroma

from src.core.application.exceptions import DocumentNotFoundError, TutorNotFoundError
from src.core.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    DocumentServiceProtocol,
    TutorRepositoryProtocol,
)
from src.core.domain.models import Document
from src.core.infrastructure.constants import PROJECT_ROOT

logger = logging.getLogger(__name__)


class DocumentService(DocumentServiceProtocol):
    """
    Manages the lifecycle of documents, including deletion and garbage collection
    of both database records and physical files.
    """

    def __init__(
        self,
        doc_repo: DocumentRepositoryProtocol,
        chunk_repo: ChunkRepositoryProtocol,
        tutor_repo: TutorRepositoryProtocol,
        vector_store: Chroma,
    ):
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.tutor_repo = tutor_repo
        self.vector_store = vector_store

    def delete_document_from_tutor(self, document_id: int, tutor_id: int) -> None:
        """
        Removes a document's link to a tutor and, if the document becomes
        orphaned, triggers a full garbage collection.
        """
        tutor = self.tutor_repo.get_tutor_by_id(tutor_id)
        if not tutor:
            raise TutorNotFoundError(tutor_id=tutor_id)

        document = self.doc_repo.get_document_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(document_id=document_id)

        self.tutor_repo.remove_document_from_tutor(tutor, document)

        # After unlinking, re-fetch to get the updated relationship count
        updated_document = self.doc_repo.get_document_by_id(document_id)
        if updated_document and not updated_document.tutors:
            self._garbage_collect_orphaned_document(updated_document)

    def handle_potential_orphan(self, document_id: int) -> None:
        """
        Checks if a document is orphaned and, if so, performs garbage collection.
        """
        db_doc = self.doc_repo.get_document_by_id(document_id)
        if db_doc and not db_doc.tutors:
            self._garbage_collect_orphaned_document(db_doc)

    def _garbage_collect_orphaned_document(self, document: Document) -> None:
        """
        Private helper to perform all cleanup for an orphaned document.
        """
        logger.info(
            f"Document {document.id} ('{document.file_name}') is orphaned. "
            "Starting full garbage collection."
        )

        # Delete the physical file from storage
        if document.storage_path:
            absolute_file_path = PROJECT_ROOT / document.storage_path
            try:
                if os.path.exists(absolute_file_path):
                    os.remove(absolute_file_path)
                    logger.info(f"Deleted physical file: {absolute_file_path}")
                else:
                    logger.warning(
                        f"Orphaned file not found at path: {absolute_file_path}"
                    )
            except OSError as e:
                logger.error(
                    f"Error deleting file {absolute_file_path}: {e}", exc_info=True
                )

        # Find and delete chunks from vector store
        orphaned_chunks = self.chunk_repo.get_orphaned_chunks(document)
        chunk_hashes_to_delete = [c.content_hash for c in orphaned_chunks]
        if chunk_hashes_to_delete:
            self.vector_store.delete(ids=chunk_hashes_to_delete)
            logger.info(f"Garbage collected {len(chunk_hashes_to_delete)} chunks.")

        # Delete the records from the relational database
        self.doc_repo.delete_document(document)
        logger.info(f"Deleted Document record {document.id} from database.")
