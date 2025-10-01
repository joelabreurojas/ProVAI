from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.api.tutor.application.services import TutorService
from src.core.application.exceptions import (
    InsufficientPermissionsError,
    InvitationEmailMismatchError,
    InvitationNotFoundError,
    SelfEnrollmentError,
    UserAlreadyEnrolledError,
)
from src.core.application.protocols import (
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.core.domain.models import Document, Tutor, User
from src.core.domain.schemas import TutorCreate


def create_mocked_tutor_service(
    mocker: MockerFixture,
) -> tuple[TutorServiceProtocol, dict[str, MagicMock]]:
    """Creates a TutorService with its TutorRepository dependency mocked."""
    mock_tutor_repo = mocker.MagicMock(spec=TutorRepositoryProtocol)

    service = TutorService(tutor_repo=mock_tutor_repo)

    mocks = {"tutor_repo": mock_tutor_repo}
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


def test_add_students_to_invitation(mocker: MockerFixture) -> None:
    """Tests that new students are correctly added to the tutor's whitelist."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_teacher = mocker.MagicMock(spec=User, id=101, role="teacher")
    mock_tutor = mocker.MagicMock(
        spec=Tutor, id=1, teacher_id=101, token="a_real_token"
    )

    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor

    emails_to_add = ["student_a@test.com", "student_b@test.com"]
    service.add_authorized_students(1, mock_teacher, emails_to_add)

    mocks["tutor_repo"].add_authorized_emails.assert_called_once_with(
        mock_tutor, emails_to_add
    )


def test_enroll_student_successfully(mocker: MockerFixture) -> None:
    """Tests the happy path for a student successfully enrolling."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User, id=202, email="student@test.com")
    mock_tutor = mocker.MagicMock(id=1, teacher_id=101, students=[])

    mocks["tutor_repo"].get_tutor_by_token.return_value = mock_tutor
    mocks["tutor_repo"].get_authorized_emails.return_value = ["student@test.com"]

    service.enroll_student_from_token("valid_token", mock_student)

    mocks["tutor_repo"].add_student_to_tutor.assert_called_once_with(
        mock_tutor, mock_student
    )


def test_enroll_student_fails_if_token_is_invalid(mocker: MockerFixture) -> None:
    """Tests that enrollment fails with a specific error if the token does not exist."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User)

    mocks["tutor_repo"].get_tutor_by_token.return_value = None

    with pytest.raises(InvitationNotFoundError):
        service.enroll_student_from_token("non_existent_token", mock_student)


def test_enroll_student_fails_if_email_not_on_list(mocker: MockerFixture) -> None:
    """Tests that enrollment fails if the user's email is not on the invitation list."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_unauthorized_student = mocker.MagicMock(spec=User, email="hacker@test.com")
    mock_tutor = mocker.MagicMock(spec=Tutor)

    mocks["tutor_repo"].get_tutor_by_token.return_value = mock_tutor
    # The student's email is not in the returned whitelist
    mocks["tutor_repo"].get_authorized_emails.return_value = ["authorized@test.com"]

    with pytest.raises(InvitationEmailMismatchError):
        service.enroll_student_from_token("any_token", mock_unauthorized_student)


def test_link_document_to_tutor_calls_repository(mocker: MockerFixture) -> None:
    """Tests that the service correctly passes through to the repository."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_tutor = mocker.MagicMock(spec=Tutor)
    mock_document = mocker.MagicMock(spec=Document)

    service.link_document_to_tutor(mock_tutor, mock_document)

    mocks["tutor_repo"].link_document_to_tutor.assert_called_once_with(
        mock_tutor, mock_document
    )


def test_enroll_student_fails_if_already_enrolled(mocker: MockerFixture) -> None:
    """
    Tests that UserAlreadyEnrolledError is raised if a student attempts to
    enroll in a Tutor they are already a member of.
    """
    service, mocks = create_mocked_tutor_service(mocker)

    mock_student = mocker.MagicMock(spec=User, id=202, email="student@test.com")
    # Simulate a tutor where this student is already in the students list
    mock_tutor = mocker.MagicMock(
        spec=Tutor, id=1, teacher_id=101, students=[mock_student]
    )

    mocks["tutor_repo"].get_tutor_by_token.return_value = mock_tutor
    mocks["tutor_repo"].get_authorized_emails.return_value = ["student@test.com"]

    with pytest.raises(UserAlreadyEnrolledError):
        service.enroll_student_from_token("valid_token_for_enrolled_user", mock_student)

    # Assert that the database was NOT written to again
    mocks["tutor_repo"].add_student_to_tutor.assert_not_called()


def test_enroll_student_fails_if_user_is_the_teacher(mocker: MockerFixture) -> None:
    """
    Tests that SelfEnrollmentError is raised if a user who is the teacher of a
    Tutor attempts to enroll in it as a student.
    """
    service, mocks = create_mocked_tutor_service(mocker)

    # The user trying to enroll is the teacher of the course
    mock_teacher_as_student = mocker.MagicMock(
        spec=User, id=101, email="teacher@test.com"
    )
    mock_tutor = mocker.MagicMock(spec=Tutor, id=1, teacher_id=101, students=[])

    mocks["tutor_repo"].get_tutor_by_token.return_value = mock_tutor
    mocks["tutor_repo"].get_authorized_emails.return_value = ["teacher@test.com"]

    with pytest.raises(SelfEnrollmentError):
        service.enroll_student_from_token(
            "valid_token_for_teacher", mock_teacher_as_student
        )

    # Verify no database writes were attempted
    mocks["tutor_repo"].add_student_to_tutor.assert_not_called()
