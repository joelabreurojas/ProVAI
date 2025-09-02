from sqlalchemy.orm import Session

from src.api.auth.domain.models import User
from src.api.chat.infrastructure.repositories import SQLAlchemyChatRepository
from src.api.tutor.domain.models import Tutor


def test_create_and_retrieve_chat(db_session: Session) -> None:
    """Tests that a chat can be created and then retrieved."""
    teacher = User(name="T", email="t@t.com", hashed_password="pw")
    student = User(name="S", email="s@s.com", hashed_password="pw")
    tutor = Tutor(course_name="Test Course", teacher=teacher)
    db_session.add_all([teacher, student, tutor])
    db_session.commit()

    repo = SQLAlchemyChatRepository(db_session)

    new_chat = repo.create_chat(
        tutor_id=tutor.id, user_id=student.id, title="My Test Chat"
    )

    assert new_chat.id is not None
    assert new_chat.title == "My Test Chat"

    retrieved_chat = repo.get_chat_by_id(new_chat.id)
    assert retrieved_chat is not None
    assert retrieved_chat.id == new_chat.id


def test_add_message_to_chat(db_session: Session) -> None:
    """Tests that messages can be successfully added to a chat."""
    teacher = User(name="T", email="t@t.com", hashed_password="pw")
    student = User(name="S", email="s@s.com", hashed_password="pw")
    tutor = Tutor(course_name="Test Course", teacher=teacher)
    db_session.add_all([teacher, student, tutor])
    db_session.commit()
    repo = SQLAlchemyChatRepository(db_session)
    chat = repo.create_chat(tutor.id, student.id, "Test")

    repo.add_message(chat.id, "user", "Hello")
    repo.add_message(chat.id, "tutor", "Hi there")

    db_session.refresh(chat)
    assert len(chat.messages) == 2
    assert chat.messages[0].content == "Hello"
    assert chat.messages[1].role == "tutor"
