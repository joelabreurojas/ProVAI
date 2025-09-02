import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.api.chat.domain.models import Chat


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    role: Mapped[str]  # "user" or "tutor"
    content: Mapped[str]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.UTC)
    )
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
