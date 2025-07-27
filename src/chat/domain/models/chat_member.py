from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.chat.domain.models import Chat


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
