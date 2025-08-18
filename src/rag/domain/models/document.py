import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base
from src.rag.domain.models.links import chat_document_link, document_chunk_link

if TYPE_CHECKING:
    from src.chat.domain.models.chat import Chat
    from src.rag.domain.models.chunk import Chunk


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    chats: Mapped[list["Chat"]] = relationship(
        secondary=chat_document_link, back_populates="documents"
    )
    chunks: Mapped[list["Chunk"]] = relationship(
        secondary=document_chunk_link, back_populates="documents"
    )
