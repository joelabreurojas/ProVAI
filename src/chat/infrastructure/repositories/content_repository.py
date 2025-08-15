from sqlalchemy.orm import Session as SQLAlchemySession

from src.chat.application.protocols import ContentRepositoryProtocol
from src.chat.domain.models import Chat, Chunk, Document


class SQLAlchemyContentRepository(ContentRepositoryProtocol):
    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def create_document(self, file_name: str, chat_id: int) -> Document:
        # Find the chat to associate with
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            # In a real app, we'd raise a custom ChatNotFoundError
            raise ValueError(f"Chat with id {chat_id} not found.")

        db_document = Document(file_name=file_name)
        # Create the many-to-many link
        chat.documents.append(db_document)

        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def get_chunk_by_hash(self, content_hash: str) -> Chunk | None:
        return self.db.query(Chunk).filter_by(content_hash=content_hash).first()

    def create_chunk(self, content_hash: str) -> Chunk:
        db_chunk = Chunk(content_hash=content_hash)
        self.db.add(db_chunk)
        # We can commit here or do it in a batch later
        self.db.commit()
        self.db.refresh(db_chunk)
        return db_chunk

    def link_chunk_to_document(self, db_document: Document, db_chunk: Chunk) -> None:
        # The beauty of SQLAlchemy relationships - just append
        db_document.chunks.append(db_chunk)
        self.db.commit()
