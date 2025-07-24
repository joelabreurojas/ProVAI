import pytest
from sqlalchemy.orm import Session

from src.application.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from src.application.services.auth_service import AuthService
from src.domain.schemas import UserCreate

from src.infrastructure.security import get_password_hash, verify_password


@pytest.fixture
def auth_service(db_session: Session) -> AuthService:
    """Fixture to create an AuthService instance."""
    return AuthService(db_session, get_password_hash, verify_password)


def test_register_user_success(db_session: Session) -> None:
    """Tests successful user registration."""
    auth_service = AuthService(db_session)
    user_data = UserCreate(
        name="Test User", email="test@example.com", password="password123"
    )

    new_user = auth_service.register_user(user_data)

    assert new_user.name == user_data.name
    assert new_user.email == user_data.email
    assert new_user.id is not None
    assert auth_service.verify_password(user_data.password, new_user.hashed_password)


def test_register_duplicate_user_fails(db_session: Session) -> None:
    """Tests that registering a user with an existing email raises an error."""
    auth_service = AuthService(db_session)
    user_data = UserCreate(
        name="Test User", email="test@example.com", password="password123"
    )

    auth_service.register_user(user_data)

    # Attempt to register the same user again
    with pytest.raises(UserAlreadyExistsError):
        auth_service.register_user(user_data)


def test_authenticate_user_success(db_session: Session) -> None:
    """Tests successful user authentication with correct credentials."""
    auth_service = AuthService(db_session)
    user_data = UserCreate(
        name="Test User", email="test@example.com", password="password123"
    )

    new_user = auth_service.register_user(user_data)

    authenticated_user = auth_service.authenticate_user(
        user_data.email, user_data.password
    )

    assert authenticated_user is not None
    assert authenticated_user.email == new_user.email


def test_authenticate_user_wrong_password_fails(db_session: Session):
    """Tests that authentication fails with an incorrect password."""
    auth_service = AuthService(db_session)
    user_data = UserCreate(
        name="Test User", email="test@example.com", password="password123"
    )

    auth_service.register_user(user_data)

    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate_user(user_data.email, "wrong_password")
