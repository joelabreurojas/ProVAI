from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.chat.domain.models import Chat, ChatMember  # Import for type hints


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="student", nullable=False)

    chats: Mapped[list["Chat"]] = relationship(back_populates="owner")
    chat_memberships: Mapped[list["ChatMember"]] = relationship(back_populates="user")
