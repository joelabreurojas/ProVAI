from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.core.domain.models import Tutor


class Invitation(Base):
    """
    The whitelist of emails authorized to enroll in a specific Tutor.
    It is a simple association table.
    """

    __tablename__ = "invitations"

    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutors.id"), primary_key=True)
    student_email: Mapped[str] = mapped_column(primary_key=True)

    tutor: Mapped["Tutor"] = relationship(back_populates="authorized_students")
