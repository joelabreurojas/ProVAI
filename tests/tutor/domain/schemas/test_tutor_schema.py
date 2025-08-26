import pytest
from pydantic import ValidationError

from src.tutor.domain.schemas import TutorCreate


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
