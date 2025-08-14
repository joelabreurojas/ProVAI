from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.infrastructure.database import Base

# Association table for the many-to-many relationship between Chat and Document
chat_document_link = Table(
    "chat_document_link",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
)

# Association table for the many-to-many relationship between Document and Chunk
document_chunk_link = Table(
    "document_chunk_link",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("chunk_id", Integer, ForeignKey("chunks.id"), primary_key=True),
)
