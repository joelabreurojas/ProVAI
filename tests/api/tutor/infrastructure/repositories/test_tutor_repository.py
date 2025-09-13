from sqlalchemy.orm import Session

from src.api.tutor.infrastructure.repositories import SQLAlchemyTutorRepository
from src.core.domain.models import User
from src.core.domain.schemas import TutorCreate


def test_create_tutor_successfully(db_session: Session) -> None:
    """Tests that a new Tutor can be created and linked to a teacher."""
    teacher = User(name="Test Teacher", email="teacher@test.com", hashed_password="pw")
    db_session.add(teacher)
    db_session.commit()

    repo = SQLAlchemyTutorRepository(db_session)
    tutor_schema = TutorCreate(course_name="Test Course")

    new_tutor = repo.create_tutor(tutor_schema, teacher.id)

    assert new_tutor.id is not None
    assert new_tutor.course_name == "Test Course"
    assert new_tutor.teacher_id == teacher.id


def test_add_student_to_tutor(db_session: Session) -> None:
    """Tests the many-to-many relationship for enrolling a student."""
    teacher = User(name="T", email="t@t.com", hashed_password="pw")
    student = User(name="S", email="s@s.com", hashed_password="pw")
    db_session.add_all([teacher, student])
    db_session.commit()

    repo = SQLAlchemyTutorRepository(db_session)
    tutor_schema = TutorCreate(course_name="Test Course")
    tutor = repo.create_tutor(tutor_schema, teacher.id)

    repo.add_student_to_tutor(tutor, student)
    db_session.refresh(tutor)  # Refresh to load the new relationship

    assert student in tutor.students
    assert len(tutor.students) == 1
