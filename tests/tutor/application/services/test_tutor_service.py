from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.auth.application.exceptions import (
    InsufficientPermissionsError,
    TokenInvalidScopeError,
)
from src.auth.application.protocols import TokenServiceProtocol
from src.auth.domain.models import User
from src.tutor.application.exceptions import (
    SelfEnrollmentError,
    TutorOwnershipError,
    UserAlreadyEnrolledError,
)
from src.tutor.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.tutor.application.services import TutorService
from src.tutor.domain.models import Tutor
from src.tutor.domain.schemas import TutorCreate


def create_mocked_tutor_service(
    mocker: MockerFixture,
) -> tuple[TutorServiceProtocol, dict[str, MagicMock]]:
    """Creates a TutorService with all its dependencies mocked."""
    mock_tutor_repo = mocker.MagicMock(spec=TutorRepositoryProtocol)
    mock_token_service = mocker.MagicMock(spec=TokenServiceProtocol)

    service = TutorService(
        tutor_repo=mock_tutor_repo,
        token_service=mock_token_service,
    )

    mocks = {
        "tutor_repo": mock_tutor_repo,
        "token_service": mock_token_service,
    }
    return service, mocks


def test_create_tutor_successfully(mocker: MockerFixture) -> None:
    """Tests that a user with the 'teacher' role can create a tutor."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_teacher = mocker.MagicMock(spec=User, id=101, role="teacher")
    tutor_schema = TutorCreate(course_name="New Course")

    service.create_tutor(tutor_create=tutor_schema, teacher=mock_teacher)

    mocks["tutor_repo"].create_tutor.assert_called_once_with(
        tutor_create=tutor_schema, teacher_id=mock_teacher.id
    )


def test_create_tutor_fails_if_user_is_not_a_teacher(mocker: MockerFixture) -> None:
    """Tests that a user with the 'student' role cannot create a tutor."""
    service, _ = create_mocked_tutor_service(mocker)
    mock_student_user = mocker.MagicMock(spec=User, role="student")
    tutor_schema = TutorCreate(course_name="Illegal Course")

    with pytest.raises(InsufficientPermissionsError):
        service.create_tutor(tutor_create=tutor_schema, teacher=mock_student_user)


def test_enroll_student_successfully(mocker: MockerFixture) -> None:
    """Tests the happy path for a student successfully enrolling."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User, id=202, email="student@test.com")
    mock_tutor = mocker.MagicMock(spec=Tutor, id=1, teacher_id=101, students=[])

    valid_payload = {
        "tutor_id": 1,
        "scope": "enrollment",
        "student_email": "student@test.com",
    }
    mocks["token_service"].decode_access_token.return_value = valid_payload
    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor

    service.enroll_student(token="valid_token", student_user=mock_student)

    mocks["tutor_repo"].add_student_to_tutor.assert_called_once_with(
        mock_tutor, mock_student
    )


def test_enroll_student_fails_if_token_has_wrong_scope(mocker: MockerFixture) -> None:
    """Tests that enrollment fails if the JWT is not an enrollment token."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User)
    wrong_scope_payload = {"sub": "student@email.com", "scope": "login"}
    mocks["token_service"].decode_access_token.return_value = wrong_scope_payload

    with pytest.raises(TokenInvalidScopeError):
        service.enroll_student(
            token="a_valid_but_wrong_scope_token", student_user=mock_student
        )


def test_enroll_student_fails_if_teacher_self_enrolls(mocker: MockerFixture) -> None:
    """Tests that a teacher cannot enroll as a student in their own tutor."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_teacher = mocker.MagicMock(spec=User, id=101, email="teacher@test.com")
    mock_tutor = mocker.MagicMock(spec=Tutor, id=1, teacher_id=101, students=[])

    valid_payload = {
        "tutor_id": 1,
        "scope": "enrollment",
        "student_email": "teacher@test.com",
    }
    mocks["token_service"].decode_access_token.return_value = valid_payload
    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor

    with pytest.raises(SelfEnrollmentError):
        service.enroll_student(token="any_token", student_user=mock_teacher)


def test_enroll_student_fails_if_already_enrolled(mocker: MockerFixture) -> None:
    """Tests that a student cannot enroll in the same tutor twice."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User, id=202, email="student@test.com")
    mock_tutor = mocker.MagicMock(
        spec=Tutor, id=1, teacher_id=101, students=[mock_student]
    )

    valid_payload = {
        "tutor_id": 1,
        "scope": "enrollment",
        "student_email": "student@test.com",
    }
    mocks["token_service"].decode_access_token.return_value = valid_payload
    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor

    with pytest.raises(UserAlreadyEnrolledError):
        service.enroll_student(token="any_token", student_user=mock_student)


def test_verify_owner_succeeds_for_correct_teacher(mocker: MockerFixture) -> None:
    """Tests that verification passes for the actual owner."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_teacher = mocker.MagicMock(spec=User, id=101, role="teacher")
    mock_tutor = mocker.MagicMock(spec=Tutor, teacher_id=101)
    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor

    returned_tutor = service.verify_user_is_tutor_owner(tutor_id=1, user=mock_teacher)
    assert returned_tutor is mock_tutor


def test_verify_owner_fails_for_student(mocker: MockerFixture) -> None:
    """Tests that verification fails if the user is a student."""
    service, _ = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User, role="student")

    with pytest.raises(InsufficientPermissionsError):
        service.verify_user_is_tutor_owner(tutor_id=1, user=mock_student)


def test_verify_owner_fails_for_different_teacher(mocker: MockerFixture) -> None:
    """Tests that verification fails if the user is a different teacher."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_other_teacher = mocker.MagicMock(spec=User, id=999, role="teacher")
    mock_tutor = mocker.MagicMock(spec=Tutor, teacher_id=101)
    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor

    with pytest.raises(TutorOwnershipError):
        service.verify_user_is_tutor_owner(tutor_id=1, user=mock_other_teacher)
