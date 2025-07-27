import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.chat.domain.models import Chat


class Document(Base):
    """
    Represents a file (e.g., a PDF) that has been uploaded to a specific Chat.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    uploaded_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    chat: Mapped["Chat"] = relationship(back_populates="documents")
