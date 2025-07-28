from unittest.mock import MagicMock

import pytest

from src.auth.application.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from src.auth.application.services.auth_service import AuthService
from src.auth.domain.schemas import UserCreate


def test_register_user_success() -> None:
    mock_user_repo = MagicMock()
    mock_password_svc = MagicMock()
    mock_token_svc = MagicMock()

    # Configure mocks
    mock_user_repo.get_by_email.return_value = None  # No existing user
    mock_password_svc.get_password_hash.return_value = "hashed_password"

    auth_service = AuthService(mock_user_repo, mock_password_svc, mock_token_svc)
    user_data = UserCreate(
        name="Test User", email="test@example.com", password="password123"
    )

    auth_service.register_user(user_data)

    mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    mock_password_svc.get_password_hash.assert_called_once_with("password123")
    mock_user_repo.add.assert_called_once()


def test_register_user_fails_if_user_exists() -> None:
    mock_user_repo = MagicMock()
    mock_password_svc = MagicMock()
    mock_token_svc = MagicMock()

    mock_user_repo.get_by_email.return_value = True  # User already exists

    auth_service = AuthService(mock_user_repo, mock_password_svc, mock_token_svc)
    user_data = UserCreate(
        name="Test User", email="test@example.com", password="password123"
    )

    with pytest.raises(UserAlreadyExistsError):
        auth_service.register_user(user_data)


def test_authenticate_user_fails_with_bad_password() -> None:
    mock_user_repo = MagicMock()
    mock_password_svc = MagicMock()
    mock_token_svc = MagicMock()

    # Mock a user object that the repo would return
    mock_user = MagicMock()
    mock_user.hashed_password = "correct_hashed_password"

    mock_user_repo.get_by_email.return_value = mock_user
    mock_password_svc.verify_password.return_value = (
        False  # Password verification fails
    )

    auth_service = AuthService(mock_user_repo, mock_password_svc, mock_token_svc)

    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate_user("test@example.com", "wrong_password")
