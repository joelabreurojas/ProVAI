from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.chat.domain.models import Assistant


class Enrollment(Base):
    __tablename__ = "enrollments"

    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistants.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role: Mapped[str]  # "teacher" or "student"

    assistant: Mapped["Assistant"] = relationship(back_populates="enrollments")
    user: Mapped["User"] = relationship(back_populates="enrollments")

    __table_args__ = (PrimaryKeyConstraint("assistant_id", "user_id"),)
