import logging

from langchain_chroma import Chroma

from src.core.application.exceptions import DocumentNotFoundError, TutorNotFoundError
from src.core.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    DocumentServiceProtocol,
    TutorRepositoryProtocol,
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
        tutor_repo: TutorRepositoryProtocol,
        vector_store: Chroma,
    ):
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.tutor_repo = tutor_repo
        self.vector_store = vector_store

    def delete_document_from_tutor(self, document_id: int, tutor_id: int) -> None:
        """
        Removes a document's link to a tutor and performs garbage collection
        on any chunks that are no longer referenced by any other documents.
        """
        tutor = self.tutor_repo.get_tutor_by_id(tutor_id)
        if not tutor:
            raise TutorNotFoundError(tutor_id=tutor_id)

        document = self.doc_repo.get_document_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(document_id=document_id)

        self.tutor_repo.remove_document_from_tutor(tutor, document)

        if not document.tutors:
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

    def handle_potential_orphan(self, document_id: int) -> None:
        """
        Checks if a document is orphaned (not linked to any tutors) and, if so,
        performs a full garbage collection on it and its exclusive chunks.
        """
        # Re-fetch the document from the DB to get its current, accurate state.
        db_doc = self.doc_repo.get_document_by_id(document_id)

        # If the document was already deleted by another process, or if it's
        # still linked to other tutors, do nothing.
        if not db_doc or db_doc.tutors:
            return

        logger.info(f"Document {document_id} is confirmed orphaned. Starting GC.")

        # Same GC logic from delete_document_from_tutor
        orphaned_chunks = self.chunk_repo.get_orphaned_chunks(db_doc)
        chunk_hashes_to_delete = [c.content_hash for c in orphaned_chunks]

        # Delete from relational DB
        if orphaned_chunks:
            self.chunk_repo.delete_chunks(orphaned_chunks)
        self.doc_repo.delete_document(db_doc)

        # Delete from vector store
        if chunk_hashes_to_delete:
            self.vector_store.delete(ids=chunk_hashes_to_delete)
            logger.info(
                f"Garbage collected {len(chunk_hashes_to_delete)} "
                "orphaned chunks from vector store."
            )
