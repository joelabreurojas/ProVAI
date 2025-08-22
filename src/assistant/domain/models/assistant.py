from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base
from src.rag.domain.models.links import assistant_document_link

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.chat.domain.models import Chat, Document, Enrollment


class Assistant(Base):
    __tablename__ = "assistants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    roadmap: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    teacher: Mapped["User"] = relationship(back_populates="created_assistants")

    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="assistant")
    documents: Mapped[list["Document"]] = relationship(
        secondary=assistant_document_link, back_populates="assistants"
    )
    chats: Mapped[list["Chat"]] = relationship(back_populates="assistant")
