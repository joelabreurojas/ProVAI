from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base
from src.tutor.domain.models.links import tutor_students

if TYPE_CHECKING:
    from src.chat.domain.models import Chat, Tutor


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="student", nullable=False)
    profile: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    created_tutors: Mapped[list["Tutor"]] = relationship(back_populates="teacher")
    enrolled_tutors: Mapped[list["Tutor"]] = relationship(
        secondary=tutor_students, back_populates="students"
    )
    chats: Mapped[list["Chat"]] = relationship(back_populates="user")
