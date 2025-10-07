import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.domain.models.tutor import tutor_document
from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.core.domain.models import Chunk, Tutor

document_chunk = Table(
    "document_chunk",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("chunk_id", Integer, ForeignKey("chunks.id"), primary_key=True),
)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.UTC)
    )

    tutors: Mapped[list["Tutor"]] = relationship(
        secondary=tutor_document, back_populates="documents"
    )
    chunks: Mapped[list["Chunk"]] = relationship(
        secondary=document_chunk, back_populates="documents"
    )
