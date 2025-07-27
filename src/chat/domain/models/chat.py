import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.chat.domain.models import ChatMember, Document, SessionHistory


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
