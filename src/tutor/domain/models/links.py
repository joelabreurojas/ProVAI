from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.tutor.domain.models import Invitation

tutor_students = Table(
    "tutor_students",
    Base.metadata,
    Column("tutor_id", Integer, ForeignKey("tutors.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class InvitationMember(Base):
    """
    An association object that links a student's email to a specific
    invitation and tracks their enrollment status through that invitation.
    """

    __tablename__ = "invitation_members"

    invitation_id: Mapped[int] = mapped_column(
        ForeignKey("invitations.id"), primary_key=True
    )
    student_email: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)

    invitation: Mapped["Invitation"] = relationship(back_populates="members")
