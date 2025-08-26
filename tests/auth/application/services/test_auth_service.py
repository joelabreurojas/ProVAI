import pytest
from pytest_mock import MockerFixture

from src.auth.application.exceptions import (
    InvalidCredentialsError,
    TokenValidationError,
    UserAlreadyExistsError,
)
from src.auth.application.protocols import (
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.auth.application.services import AuthService
from src.auth.domain.schemas import UserCreate

VALID_PASSWORD = "ValidPassword123!"


def test_register_user_successfully(mocker: MockerFixture) -> None:
    """
    Tests that a user is registered successfully when the email is not already in use.
    """
    mock_user_repo = mocker.MagicMock(spec=UserRepositoryProtocol)
    mock_password_svc = mocker.MagicMock(spec=PasswordServiceProtocol)
    mock_token_svc = mocker.MagicMock(spec=TokenServiceProtocol)

    mock_user_repo.get_by_email.return_value = None  # Simulate user not found
    mock_password_svc.get_password_hash.return_value = "hashed_password"

    auth_service = AuthService(mock_user_repo, mock_password_svc, mock_token_svc)
    user_data = UserCreate(
        name="Test User", email="test@example.com", password=VALID_PASSWORD
    )

    auth_service.register_user(user_data)

    mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    mock_password_svc.get_password_hash.assert_called_once_with(VALID_PASSWORD)
    mock_user_repo.add.assert_called_once()


def test_register_user_fails_if_email_exists(mocker: MockerFixture) -> None:
    """
    Tests that UserAlreadyExistsError is raised if the user's email already exists.
    """
    mock_user_repo = mocker.MagicMock(spec=UserRepositoryProtocol)

    # Simulate finding an existing user
    mock_user_repo.get_by_email.return_value = mocker.MagicMock()

    auth_service = AuthService(mock_user_repo, mocker.MagicMock(), mocker.MagicMock())
    user_data = UserCreate(
        name="Test User", email="test@example.com", password=VALID_PASSWORD
    )

    with pytest.raises(UserAlreadyExistsError):
        auth_service.register_user(user_data)


def test_authenticate_user_fails_with_bad_password(mocker: MockerFixture) -> None:
    """
    Tests that InvalidCredentialsError is raised if the password verification fails.
    """
    mock_user_repo = mocker.MagicMock(spec=UserRepositoryProtocol)
    mock_password_svc = mocker.MagicMock(spec=PasswordServiceProtocol)

    mock_user = mocker.MagicMock()
    mock_user.hashed_password = "correct_hashed_password"
    mock_user_repo.get_by_email.return_value = mock_user
    mock_password_svc.verify_password.return_value = False  # Simulate password mismatch

    auth_service = AuthService(mock_user_repo, mock_password_svc, mocker.MagicMock())

    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate_user("test@example.com", "wrong_password")

    mock_password_svc.verify_password.assert_called_once_with(
        "wrong_password", "correct_hashed_password"
    )


def test_get_user_from_token_fails_if_user_not_found(mocker: MockerFixture) -> None:
    """
    Tests that token validation fails if the email in the token payload
    does not correspond to an existing user (e.g., user was deleted).
    """
    mock_user_repo = mocker.MagicMock(spec=UserRepositoryProtocol)
    mock_token_svc = mocker.MagicMock(spec=TokenServiceProtocol)

    # Simulate a valid token payload for a user that no longer exists
    valid_payload = {"sub": "deleted-user@example.com"}
    mock_token_svc.decode_access_token.return_value = valid_payload
    mock_user_repo.get_by_email.return_value = None

    auth_service = AuthService(mock_user_repo, mocker.MagicMock(), mock_token_svc)

    with pytest.raises(TokenValidationError):
        auth_service.get_user_from_token("any_valid_token")
