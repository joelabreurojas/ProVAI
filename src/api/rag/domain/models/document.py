import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.core.infrastructure.database import Base
from src.api.rag.domain.models.links import document_chunk_link, tutor_document_link

if TYPE_CHECKING:
    from src.api.rag.domain.models import Chunk
    from src.api.tutor.domain.models import Tutor


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.UTC)
    )

    tutors: Mapped[list["Tutor"]] = relationship(
        secondary=tutor_document_link, back_populates="documents"
    )
    chunks: Mapped[list["Chunk"]] = relationship(
        secondary=document_chunk_link, back_populates="documents"
    )
