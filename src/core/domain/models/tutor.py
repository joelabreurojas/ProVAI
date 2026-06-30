import secrets
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from .chat import Chat
    from .document import Document
    from .invitation import Invitation
    from .user import User

tutor_document = Table(
    "tutor_document",
    Base.metadata,
    Column("tutor_id", Integer, ForeignKey("tutors.id"), primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
)

tutor_students = Table(
    "tutor_students",
    Base.metadata,
    Column("tutor_id", Integer, ForeignKey("tutors.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Tutor(Base):
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_name: Mapped[str] = mapped_column(index=True)
    token: Mapped[str] = mapped_column(
        unique=True, index=True, default=lambda: secrets.token_urlsafe(32)
    )
    description: Mapped[str | None]
    roadmap: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    teacher: Mapped["User"] = relationship(back_populates="created_tutors")

    students: Mapped[list["User"]] = relationship(
        secondary=tutor_students, back_populates="enrolled_tutors"
    )
    documents: Mapped[list["Document"]] = relationship(
        secondary=tutor_document, back_populates="tutors"
    )
    chats: Mapped[list["Chat"]] = relationship(
        back_populates="tutor",
        cascade="all, delete-orphan",
    )
    authorized_students: Mapped[list["Invitation"]] = relationship(
        back_populates="tutor", cascade="all, delete-orphan"
    )
