from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base
from src.rag.domain.models.links import tutor_document_link
from src.tutor.domain.models.links import tutor_students

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.chat.domain.models import Chat
    from src.rag.domain.models import Document


class Tutor(Base):
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str | None]
    roadmap: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    teacher: Mapped["User"] = relationship(back_populates="created_tutors")

    students: Mapped[list["User"]] = relationship(
        secondary=tutor_students, back_populates="enrolled_tutors"
    )
    documents: Mapped[list["Document"]] = relationship(
        secondary=tutor_document_link, back_populates="tutors"
    )
    chats: Mapped[list["Chat"]] = relationship(back_populates="tutor")
