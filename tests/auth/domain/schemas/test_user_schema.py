import pytest
from pydantic import ValidationError

from src.auth.domain.schemas import UserCreate


def test_user_create_success() -> None:
    """Tests that a valid user schema passes validation."""
    try:
        UserCreate(
            name="Valid User",
            email="valid@example.com",
            password="ValidPassword123!",
        )
    except ValidationError as e:
        pytest.fail(f"Valid user schema raised an unexpected error: {e}")


@pytest.mark.parametrize(
    ("password", "expected_error"),
    [
        ("short", "at least 8 characters"),
        ("nouppercase1!", "at least one uppercase letter"),
        ("NOLOWERCASE1!", "at least one lowercase letter"),
        ("NoNumber!", "at least one number"),
        ("NoSpecial123", "at least one special character"),
    ],
)
def test_user_create_password_complexity_fails(
    password: str, expected_error: str
) -> None:
    """
    Tests that passwords failing complexity requirements raise a ValidationError
    with a helpful message.
    """
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            name="Test User",
            email="test@example.com",
            password=password,
        )
    assert expected_error in str(exc_info.value)


def test_user_create_invalid_email_fails() -> None:
    """Tests that an invalid email format raises a ValidationError."""
    with pytest.raises(ValidationError):
        UserCreate(
            name="Test User",
            email="not-an-email",
            password="ValidPassword123!",
        )
