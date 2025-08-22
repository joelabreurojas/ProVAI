from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.infrastructure.database import Base

assistant_document_link = Table(
    "assistant_document_link",
    Base.metadata,
    Column("assistant_id", Integer, ForeignKey("assistants.id"), primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
)

document_chunk_link = Table(
    "document_chunk_link",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("chunk_id", Integer, ForeignKey("chunks.id"), primary_key=True),
)
