from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.core.domain.models import Invitation


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
