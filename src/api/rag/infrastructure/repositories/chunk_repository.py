from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.application.protocols import ChunkRepositoryProtocol
from src.core.domain.models import Chunk, Document


class SQLAlchemyChunkRepository(ChunkRepositoryProtocol):
    """Concrete implementation of the Chunk repository using SQLAlchemy."""

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def create_chunk(self, content_hash: str) -> Chunk:
        """
        Creates and adds a new Chunk to the database session, but does NOT commit.
        The service layer is responsible for the transaction boundary.
        """
        db_chunk = Chunk(content_hash=content_hash)
        self.db.add(db_chunk)
        return db_chunk

    def get_chunk_by_hash(self, content_hash: str) -> Chunk | None:
        return self.db.query(Chunk).filter_by(content_hash=content_hash).first()

    def get_existing_chunks_by_hashes(self, content_hashes: list[str]) -> set[str]:
        """
        Takes a list of hashes and returns a set of the ones that already
        exist in the database.
        """
        existing = (
            self.db.query(Chunk.content_hash)
            .filter(Chunk.content_hash.in_(content_hashes))
            .all()
        )
        return {h[0] for h in existing}

    def get_many_chunks_by_document(self, document: Document) -> list[Chunk]:
        return document.chunks

    def get_orphaned_chunks(self, document: Document) -> list[Chunk]:
        """Finds chunks that were linked to this document and are now orphaned."""
        orphans = []
        for chunk in document.chunks:
            if len(chunk.documents) == 1 and chunk.documents[0].id == document.id:
                orphans.append(chunk)
        return orphans

    def delete_chunks(self, chunks: list[Chunk]) -> None:
        """
        Deletes a list of chunk objects from the database session, but does NOT commit.
        """
        for chunk in chunks:
            self.db.delete(chunk)
