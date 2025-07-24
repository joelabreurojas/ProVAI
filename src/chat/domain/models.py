import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.auth.domain.models import User


class Chat(Base):
    """
    Represents a top-level conversation container or "classroom".
    It is owned by a single User (a "teacher").
    """

    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    # SQLAlchemy will resolve the string "User" to the User class in the `auth` module.
    owner: Mapped["User"] = relationship(back_populates="chats")

    # Relationships to other models within this `chat` domain.
    documents: Mapped[list["Document"]] = relationship(back_populates="chat")
    members: Mapped[list["ChatMember"]] = relationship(back_populates="chat")
    history: Mapped[list["SessionHistory"]] = relationship(back_populates="chat")


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


class ChatMember(Base):
    """
    An association table linking a User (a "student") to a Chat they have
    been granted access to.
    """

    __tablename__ = "chat_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    chat: Mapped["Chat"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="chat_memberships")


class SessionHistory(Base):
    """Represents a single turn in a conversation within a Chat."""

    __tablename__ = "session_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    query: Mapped[str]
    response: Mapped[str]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    chat: Mapped["Chat"] = relationship(back_populates="history")
