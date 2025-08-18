import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base
from src.rag.domain.models.links import chat_document_link

if TYPE_CHECKING:
    from src.auth.domain.models.chat_member import ChatMember
    from src.auth.domain.models.user import User
    from src.chat.domain.models.session import Session
    from src.rag.domain.models.document import Document


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

    owner: Mapped["User"] = relationship(back_populates="chats")

    members: Mapped[list["ChatMember"]] = relationship(back_populates="chat")
    documents: Mapped[list["Document"]] = relationship(
        secondary=chat_document_link, back_populates="chats"
    )
    sessions: Mapped[list["Session"]] = relationship(back_populates="chat")
