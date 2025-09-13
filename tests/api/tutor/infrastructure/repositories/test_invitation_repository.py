from sqlalchemy.orm import Session as SQLAlchemySesison

from src.api.tutor.infrastructure.repositories import (
    SQLAlchemyInvitationRepository,
    SQLAlchemyTutorRepository,
)
from src.core.domain.models import User
from src.core.domain.schemas import TutorCreate


def test_create_and_retrieve_invitation(db_session: SQLAlchemySesison) -> None:
    """
    Tests that an invitation can be created and then retrieved by token and tutor_id.
    """
    teacher = User(name="T", email="t@t.com", hashed_password="pw", role="teacher")
    db_session.add(teacher)
    db_session.commit()

    tutor_schema = TutorCreate(course_name="Test Course")
    tutor = SQLAlchemyTutorRepository(db_session).create_tutor(
        tutor_create=tutor_schema, teacher_id=teacher.id
    )

    repo = SQLAlchemyInvitationRepository(db_session)

    new_invitation = repo.create_for_tutor(tutor.id)

    assert new_invitation.id is not None
    assert new_invitation.token is not None

    found_by_tutor = repo.get_by_tutor_id(tutor.id)
    found_by_token = repo.get_by_token(new_invitation.token)

    assert found_by_tutor is not None
    assert found_by_token is not None
    assert found_by_tutor.id == new_invitation.id
    assert found_by_token.id == new_invitation.id


def test_add_and_update_members(db_session: SQLAlchemySesison) -> None:
    """Tests that members can be added and their status updated."""
    teacher = User(name="T", email="t@t.com", hashed_password="pw", role="teacher")
    db_session.add(teacher)
    db_session.commit()

    tutor_schema = TutorCreate(course_name="Another Test Course")
    tutor = SQLAlchemyTutorRepository(db_session).create_tutor(
        tutor_create=tutor_schema, teacher_id=teacher.id
    )

    repo = SQLAlchemyInvitationRepository(db_session)
    invitation = repo.create_for_tutor(tutor.id)
    emails = ["student_a@test.com", "student_b@test.com"]

    repo.add_members(invitation, emails)
    db_session.refresh(invitation)

    assert len(invitation.members) == 2
    assert invitation.members[0].student_email == "student_a@test.com"
    assert invitation.members[0].status == "pending"

    repo.update_member_status(invitation, "student_a@test.com", "accepted")
    db_session.refresh(invitation)

    assert invitation.members[0].status == "accepted"
