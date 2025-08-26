from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.auth.application.exceptions import InsufficientPermissionsError
from src.auth.domain.models import User
from src.rag.domain.models import Document
from src.tutor.application.exceptions import (
    InvitationEmailMismatchError,
    InvitationNotFoundError,
)
from src.tutor.application.protocols import (
    InvitationRepositoryProtocol,
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.tutor.application.services import TutorService
from src.tutor.domain.models import Invitation, Tutor
from src.tutor.domain.schemas import TutorCreate


def create_mocked_tutor_service(
    mocker: MockerFixture,
) -> tuple[TutorServiceProtocol, dict[str, MagicMock]]:
    """Creates a TutorService with all its dependencies mocked."""
    mock_tutor_repo = mocker.MagicMock(spec=TutorRepositoryProtocol)
    mock_invitation_repo = mocker.MagicMock(spec=InvitationRepositoryProtocol)

    service = TutorService(
        tutor_repo=mock_tutor_repo,
        invitation_repo=mock_invitation_repo,
    )

    mocks = {
        "tutor_repo": mock_tutor_repo,
        "invitation_repo": mock_invitation_repo,
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


def test_get_or_create_invitation_creates_new_one(mocker: MockerFixture) -> None:
    """Tests that an invitation is created if one doesn't exist."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_teacher = mocker.MagicMock(spec=User, id=101, role="teacher")
    mock_tutor = mocker.MagicMock(spec=Tutor, id=1, teacher_id=101)

    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor
    mocks["invitation_repo"].get_by_tutor_id.return_value = None

    service.get_or_create_invitation(tutor_id=1, requesting_user=mock_teacher)

    mocks["invitation_repo"].create_for_tutor.assert_called_once_with(1)


def test_add_students_to_invitation(mocker: MockerFixture) -> None:
    """Tests that new students are correctly added to an invitation's member list."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_teacher = mocker.MagicMock(spec=User, id=101, role="teacher")
    mock_tutor = mocker.MagicMock(spec=Tutor, id=1, teacher_id=101)
    mock_invitation = mocker.MagicMock(
        spec=Invitation, id=99, tutor_id=1, token="a_real_token_string"
    )

    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor
    mocks["invitation_repo"].get_by_tutor_id.return_value = mock_invitation

    emails_to_add = ["student_a@test.com", "student_b@test.com"]
    service.add_students_to_invitation(1, mock_teacher, emails_to_add)

    mocks["invitation_repo"].add_members.assert_called_once_with(
        mock_invitation, emails_to_add
    )


def test_enroll_student_successfully(mocker: MockerFixture) -> None:
    """Tests the happy path for a student successfully enrolling."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User, id=202, email="student@test.com")
    mock_member = mocker.MagicMock(student_email="student@test.com", status="pending")
    mock_invitation = mocker.MagicMock(id=99, members=[mock_member], tutor_id=1)
    mock_tutor = mocker.MagicMock(id=1, teacher_id=101, students=[])

    mocks["invitation_repo"].get_by_token.return_value = mock_invitation
    mocks["tutor_repo"].get_tutor_by_id.return_value = mock_tutor

    service.enroll_student_from_token("valid_token", mock_student)

    mocks["tutor_repo"].add_student_to_tutor.assert_called_once_with(
        mock_tutor, mock_student
    )
    mocks["invitation_repo"].update_member_status.assert_called_once_with(
        mock_invitation, "student@test.com", "accepted"
    )


def test_enroll_student_fails_if_token_is_invalid(mocker: MockerFixture) -> None:
    """Tests that enrollment fails with a specific error if the token does not exist."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_student = mocker.MagicMock(spec=User)
    mocks["invitation_repo"].get_by_token.return_value = None

    with pytest.raises(InvitationNotFoundError):
        service.enroll_student_from_token("non_existent_token", mock_student)


def test_enroll_student_fails_if_email_not_on_list(mocker: MockerFixture) -> None:
    """Tests that enrollment fails if the user's email is not on the invitation list."""
    service, mocks = create_mocked_tutor_service(mocker)
    mock_unauthorized_student = mocker.MagicMock(spec=User, email="hacker@test.com")
    mock_member = mocker.MagicMock(
        student_email="authorized_student@test.com", status="pending"
    )
    mock_invitation = mocker.MagicMock(members=[mock_member])
    mocks["invitation_repo"].get_by_token.return_value = mock_invitation

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
