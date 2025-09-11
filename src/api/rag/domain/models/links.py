from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.infrastructure.database import Base

tutor_document_link = Table(
    "tutor_document_link",
    Base.metadata,
    Column("tutor_id", Integer, ForeignKey("tutors.id"), primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
)

document_chunk_link = Table(
    "document_chunk_link",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("chunk_id", Integer, ForeignKey("chunks.id"), primary_key=True),
)
