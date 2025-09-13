from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.api.auth.application.services import AuthService
from src.core.application.exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenMissingDataError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.core.application.protocols import (
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.core.domain.models import User


def create_mocked_auth_service(
    mocker: MockerFixture,
) -> tuple[AuthService, dict[str, MagicMock]]:
    """Creates an AuthService with all its dependencies mocked."""
    mock_user_repo = mocker.MagicMock(spec=UserRepositoryProtocol)
    mock_password_svc = mocker.MagicMock(spec=PasswordServiceProtocol)
    mock_token_svc = mocker.MagicMock(spec=TokenServiceProtocol)

    service = AuthService(
        user_repo=mock_user_repo,
        password_svc=mock_password_svc,
        token_svc=mock_token_svc,
    )

    mocks = {
        "user_repo": mock_user_repo,
        "password_svc": mock_password_svc,
        "token_service": mock_token_svc,
    }
    return service, mocks


def test_register_user_successfully(mocker: MockerFixture) -> None:
    service, mocks = create_mocked_auth_service(mocker)
    mocks["user_repo"].get_by_email.return_value = None
    mocks["password_svc"].get_password_hash.return_value = "hashed_password"
    service.register_user(
        name="Test User", email="test@example.com", password="ValidPassword123!"
    )
    mocks["user_repo"].add.assert_called_once()


def test_register_user_fails_if_email_exists(mocker: MockerFixture) -> None:
    service, mocks = create_mocked_auth_service(mocker)
    mocks["user_repo"].get_by_email.return_value = mocker.MagicMock()

    with pytest.raises(UserAlreadyExistsError):
        service.register_user(
            name="Test User", email="test@example.com", password="ValidPassword123!"
        )


def test_authenticate_user_fails_with_bad_password(mocker: MockerFixture) -> None:
    service, mocks = create_mocked_auth_service(mocker)
    mock_user = mocker.MagicMock(hashed_password="correct_hashed_password")
    mocks["user_repo"].get_by_email.return_value = mock_user
    mocks["password_svc"].verify_password.return_value = False
    with pytest.raises(InvalidCredentialsError):
        service.authenticate_user("test@example.com", "wrong_password")


def test_get_user_from_token_success(mocker: MockerFixture) -> None:
    """Tests the happy path for successfully validating a token and finding a user."""
    service, mocks = create_mocked_auth_service(mocker)
    mock_user = mocker.MagicMock(spec=User)
    valid_payload = {"sub": "test@example.com"}

    mocks["token_service"].decode_access_token.return_value = valid_payload
    mocks["user_repo"].get_by_email.return_value = mock_user

    user = service.get_user_from_token("valid_token")

    assert user is mock_user
    mocks["token_service"].decode_access_token.assert_called_once_with("valid_token")
    mocks["user_repo"].get_by_email.assert_called_once_with("test@example.com")


def test_get_user_from_token_raises_specific_error_on_expiry(
    mocker: MockerFixture,
) -> None:
    """Tests that a specific TokenExpiredError from the token service is propagated."""
    service, mocks = create_mocked_auth_service(mocker)
    mocks["token_service"].decode_access_token.side_effect = TokenExpiredError()

    with pytest.raises(TokenExpiredError):
        service.get_user_from_token("expired_token")


def test_get_user_from_token_raises_error_if_claim_is_missing(
    mocker: MockerFixture,
) -> None:
    """
    Tests that TokenMissingDataError is raised if the 'sub' claim is not in the payload.
    """
    service, mocks = create_mocked_auth_service(mocker)
    payload_without_sub = {"scope": "login"}
    mocks["token_service"].decode_access_token.return_value = payload_without_sub

    with pytest.raises(TokenMissingDataError) as exc_info:
        service.get_user_from_token("token_with_missing_data")

    assert "missing required claim: 'sub'" in str(exc_info.value)


def test_get_user_from_token_raises_error_if_user_not_found(
    mocker: MockerFixture,
) -> None:
    """
    Tests that UserNotFoundError is raised if the token is valid but the
    user it points to no longer exists.
    """
    service, mocks = create_mocked_auth_service(mocker)
    valid_payload = {"sub": "deleted@example.com"}

    mocks["token_service"].decode_access_token.return_value = valid_payload
    mocks["user_repo"].get_by_email.return_value = None

    with pytest.raises(UserNotFoundError):
        service.get_user_from_token("valid_token_for_deleted_user")
