import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.chat.domain.models import Chat


class SessionHistory(Base):
    """Represents a single turn in a conversation within a Chat."""

    __tablename__ = "session_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    query: Mapped[str]
    response: Mapped[str]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow
    )

    chat: Mapped["Chat"] = relationship(back_populates="history")
