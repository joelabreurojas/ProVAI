import secrets
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from src.core.application.protocols import InvitationRepositoryProtocol
from src.core.domain.models import Invitation
from src.core.domain.models.associations import InvitationMember


class SQLAlchemyInvitationRepository(InvitationRepositoryProtocol):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_tutor_id(self, tutor_id: int) -> Optional[Invitation]:
        return self.db.query(Invitation).filter_by(tutor_id=tutor_id).one_or_none()

    def get_by_token(self, token: str) -> Optional[Invitation]:
        return (
            self.db.query(Invitation)
            .options(joinedload(Invitation.members))
            .filter_by(token=token)
            .one_or_none()
        )

    def create_for_tutor(self, tutor_id: int) -> Invitation:
        new_token = secrets.token_urlsafe(32)
        db_invitation = Invitation(tutor_id=tutor_id, token=new_token)
        self.db.add(db_invitation)
        self.db.commit()
        self.db.refresh(db_invitation)
        return db_invitation

    def add_members(self, invitation: Invitation, student_emails: list[str]) -> None:
        existing_emails = {member.student_email for member in invitation.members}
        for email in set(student_emails):  # De-duplicate the input list
            if email not in existing_emails:
                member = InvitationMember(
                    invitation_id=invitation.id, student_email=email
                )
                self.db.add(member)
        self.db.commit()

    def update_member_status(
        self, invitation: Invitation, student_email: str, status: str
    ) -> None:
        for member in invitation.members:
            if member.student_email == student_email:
                member.status = status
                break
        self.db.commit()
