import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.api.tutor.domain.models.links import InvitationMember
    from src.api.tutor.domain.models.tutor import Tutor


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, index=True)

    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutors.id"), unique=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(datetime.UTC)
    )

    tutor: Mapped["Tutor"] = relationship(back_populates="invitation")
    members: Mapped[list["InvitationMember"]] = relationship(
        back_populates="invitation", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("tutor_id", name="uq_invitation_tutor_id"),)
