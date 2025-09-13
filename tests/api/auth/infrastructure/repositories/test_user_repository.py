from sqlalchemy.orm import Session

from src.api.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.core.domain.models import User
from src.core.domain.schemas import UserCreate

VALID_PASSWORD = "ValidPassword123!"


def test_add_user_successfully(db_session: Session) -> None:
    """
    Tests that a user can be created and committed to the database.
    This is an integration test that touches the real database session.
    """
    repo = SQLAlchemyUserRepository(db_session)
    user_schema = UserCreate(
        name="Test User", email="test@example.com", password=VALID_PASSWORD
    )
    hashed_password = "a_real_hashed_password"

    new_user = repo.add(user_schema, hashed_password)

    assert new_user.id is not None
    assert new_user.email == "test@example.com"
    assert new_user.role == "student"

    fetched_user = db_session.query(User).filter_by(id=new_user.id).one()
    assert fetched_user.name == "Test User"


def test_get_by_email_finds_user(db_session: Session) -> None:
    """Tests that an existing user can be retrieved by their email."""
    user = User(name="Find Me", email="findme@example.com", hashed_password="abc")
    db_session.add(user)
    db_session.commit()

    repo = SQLAlchemyUserRepository(db_session)
    found_user = repo.get_by_email("findme@example.com")

    assert found_user is not None
    assert found_user.id == user.id


def test_get_by_email_returns_none_for_nonexistent_user(db_session: Session) -> None:
    """Tests that None is returned for a non-existent email."""
    repo = SQLAlchemyUserRepository(db_session)
    found_user = repo.get_by_email("nobody@example.com")
    assert found_user is None
