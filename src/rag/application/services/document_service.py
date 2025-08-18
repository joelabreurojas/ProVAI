import logging

from langchain_chroma import Chroma

from src.chat.application.protocols import ChatRepositoryProtocol
from src.rag.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    DocumentServiceProtocol,
)

logger = logging.getLogger(__name__)


class DocumentService(DocumentServiceProtocol):
    def __init__(
        self,
        doc_repo: DocumentRepositoryProtocol,
        chunk_repo: ChunkRepositoryProtocol,
        chat_repo: ChatRepositoryProtocol,
        vector_store: Chroma,
    ):
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.chat_repo = chat_repo
        self.vector_store = vector_store

    def delete_document_from_chat(self, document_id: int, chat_id: int) -> None:
        """
        Deletes a document's link to a chat and performs garbage collection
        on any chunks that are no longer referenced by any documents.
        """
        # In a real app, we'd get this from a ChatRepository
        chat = self.chat_repo.get_chat_by_id(chat_id)
        document = self.doc_repo.get_document_by_id(document_id)

        if not document or not chat:
            # Or raise a specific DocumentNotFoundError
            logger.warning("Document or Chat not found for deletion.")
            return

        self.chat_repo.remove_document_from_chat(chat, document)

        if not document.chats:
            orphaned_chunks = self.chunk_repo.get_orphaned_chunks(document)
            chunk_hashes_to_delete = [c.content_hash for c in orphaned_chunks]

            if orphaned_chunks:
                self.chunk_repo.delete_chunks(orphaned_chunks)

            self.doc_repo.delete_document(document)

            if chunk_hashes_to_delete:
                self.vector_store.delete(ids=chunk_hashes_to_delete)
                logger.info(
                    f"Garbage collected {len(chunk_hashes_to_delete)} orphaned chunks."
                )
