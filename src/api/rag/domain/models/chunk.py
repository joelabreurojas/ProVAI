from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.rag.domain.models.links import document_chunk_link
from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.api.rag.domain.models import Document


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_hash: Mapped[str] = mapped_column(unique=True, index=True)

    documents: Mapped[list["Document"]] = relationship(
        secondary=document_chunk_link, back_populates="chunks"
    )
