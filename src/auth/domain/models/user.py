from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.chat.domain.models.chat import Chat
    from src.chat.domain.models.chat_member import ChatMember
    from src.chat.domain.models.session import Session


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="student", nullable=False)
    profile: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    chats: Mapped[list["Chat"]] = relationship(back_populates="owner")
    chat_memberships: Mapped[list["ChatMember"]] = relationship(back_populates="user")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
