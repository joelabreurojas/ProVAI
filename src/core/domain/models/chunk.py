from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.domain.models.document import document_chunk
from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from .document import Document


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_hash: Mapped[str] = mapped_column(unique=True, index=True)

    documents: Mapped[list["Document"]] = relationship(
        secondary=document_chunk, back_populates="chunks"
    )
