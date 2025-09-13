import pytest
from pydantic import ValidationError

from src.core.domain.schemas import TutorCreate, TutorInvitationCreate


def test_tutor_create_success() -> None:
    """Tests that a valid tutor schema passes validation."""
    try:
        TutorCreate(course_name="Valid Course Name")
    except ValidationError as e:
        pytest.fail(f"Valid tutor schema raised an unexpected error: {e}")


@pytest.mark.parametrize(
    "invalid_name",
    [
        "a",  # Too short
        "a" * 101,  # Too long
    ],
)
def test_tutor_create_name_length_fails(invalid_name: str) -> None:
    """Tests that course names failing length constraints raise a ValidationError."""
    with pytest.raises(ValidationError):
        TutorCreate(course_name=invalid_name)


def test_invitation_create_success() -> None:
    """Tests that a valid invitation schema passes validation."""
    try:
        TutorInvitationCreate(tutor_id=1, student_emails=["student@example.com"])
    except ValidationError as e:
        pytest.fail(f"Valid invitation schema raised an unexpected error: {e}")


def test_invitation_create_fails_with_invalid_email() -> None:
    """Tests that an invalid email format raises a ValidationError."""
    with pytest.raises(ValidationError):
        TutorInvitationCreate(tutor_id=1, student_emails=["not-an-email"])
