import hashlib

from sqlalchemy.orm import Session

from src.api.rag.infrastructure.repositories import (
    SQLAlchemyChunkRepository,
    SQLAlchemyDocumentRepository,
)
from src.core.domain.models import Chunk


def test_document_and_chunk_linking(db_session: Session) -> None:
    """
    Tests the core many-to-many link between documents and chunks.
    """
    doc_repo = SQLAlchemyDocumentRepository(db_session)
    chunk_repo = SQLAlchemyChunkRepository(db_session)

    doc = doc_repo.create_document("test_doc.pdf")
    chunk_hash = hashlib.sha256("test content".encode()).hexdigest()
    chunk = chunk_repo.create_chunk(chunk_hash)
    db_session.commit()

    doc_repo.link_chunk_to_document(doc, chunk)
    db_session.refresh(doc)
    db_session.refresh(chunk)

    assert chunk in doc.chunks
    assert doc in chunk.documents


def test_chunk_deduplication(db_session: Session) -> None:
    """
    Tests that get_existing_chunks_by_hashes correctly identifies
    chunks that are already in the database.
    """
    chunk_repo = SQLAlchemyChunkRepository(db_session)

    hash1 = "hash_exists"
    hash2 = "hash_does_not_exist"
    existing_chunk = Chunk(content_hash=hash1)
    db_session.add(existing_chunk)
    db_session.commit()

    found_hashes = chunk_repo.get_existing_chunks_by_hashes([hash1, hash2])

    assert found_hashes == {hash1}
