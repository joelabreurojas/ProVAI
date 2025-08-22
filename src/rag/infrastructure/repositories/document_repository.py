from sqlalchemy.orm import Session as SQLAlchemySession

from src.rag.application.protocols import DocumentRepositoryProtocol
from src.rag.domain.models import Chunk, Document


class SQLAlchemyDocumentRepository(DocumentRepositoryProtocol):
    """Concrete implementation of the Document repository using SQLAlchemy."""

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def create_document(self, file_name: str) -> Document:
        db_document = Document(file_name=file_name)
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def get_document_by_id(self, document_id: int) -> Document | None:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def link_chunk_to_document(self, db_document: Document, db_chunk: Chunk) -> None:
        """Creates the many-to-many link between a document and a chunk."""
        if db_chunk not in db_document.chunks:
            db_document.chunks.append(db_chunk)
            self.db.commit()

    def delete_document(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()
