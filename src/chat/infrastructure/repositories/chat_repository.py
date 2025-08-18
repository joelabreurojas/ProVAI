from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import joinedload

from src.chat.application.protocols import ChatRepositoryProtocol
from src.chat.domain.models import Chat
from src.rag.domain.models import Document


class SQLAlchemyChatRepository(ChatRepositoryProtocol):
    """Concrete implementation of the Chat repository using SQLAlchemy."""

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def get_chat_by_id(self, chat_id: int) -> Chat | None:
        return self.db.query(Chat).filter(Chat.id == chat_id).first()

    def link_document_to_chat(self, chat: Chat, document: Document) -> None:
        if document not in chat.documents:
            chat.documents.append(document)
            self.db.commit()

    def remove_document_from_chat(self, chat: Chat, document: Document) -> None:
        if document in chat.documents:
            chat.documents.remove(document)
            self.db.commit()

    def get_chunk_hashes_for_chat(self, chat_id: int) -> list[str]:
        """
        Performs an efficient query to get all unique content_hashes for
        all chunks related to a specific chat.
        """
        chat = (
            self.db.query(Chat)
            .options(joinedload(Chat.documents).joinedload(Document.chunks))
            .filter(Chat.id == chat_id)
            .first()
        )

        if not chat:
            return []

        # Use a set to efficiently find unique chunk hashes
        unique_chunk_hashes = {
            chunk.content_hash
            for document in chat.documents
            for chunk in document.chunks
        }

        return list(unique_chunk_hashes)
