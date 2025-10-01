import io

import fitz
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.infrastructure.settings import settings
from tests.helpers import (
    STUDENT_A_EMAIL,
    STUDENT_B_EMAIL,
    enroll_student,
    setup_users_and_tutor,
)


def test_student_cannot_add_authorized_email(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a user with the 'student' role receives a 403 Forbidden error
    if they attempt to add an authorized email to a tutor's whitelist.
    """
    context = setup_users_and_tutor(client, db_session)

    response = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}/authorized-emails",
        json={"emails": ["another@student.com"]},
        headers=context["student_a_headers"],  # Authenticated as a student
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "INSUFFICIENT_PERMISSIONS"


def test_unauthorized_student_cannot_use_invitation(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student receives a 403 Forbidden error if they try to enroll
    using a token when their email is not on the whitelist.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # The Teacher invites ONLY Student A.
    client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/authorized-emails",
        json={"emails": [STUDENT_A_EMAIL]},
        headers=context["teacher_headers"],
    )
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}",
        headers=context["teacher_headers"],
    )
    invitation_token = tutor_details_res.json()["token"]

    # Student B (the unauthorized user) tries to use the token.
    enrollment_res = client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_b_headers"],
    )

    assert enrollment_res.status_code == 403
    assert enrollment_res.json()["error_code"] == "INVITATION_EMAIL_MISMATCH"


def test_student_cannot_upload_document_to_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student, even if enrolled, cannot upload documents to a Tutor.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Enroll the student so they have access for other actions.
    enroll_student(
        client,
        tutor_id,
        STUDENT_A_EMAIL,
        context["teacher_headers"],
        context["student_a_headers"],
    )

    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.write()
    doc.close()

    upload_res = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/documents",
        files={"file": ("student_upload.pdf", pdf_bytes, "application/pdf")},
        headers=context["student_a_headers"],
    )

    assert upload_res.status_code == 403
    assert upload_res.json()["error_code"] == "INSUFFICIENT_PERMISSIONS"


def test_unenrolled_student_cannot_create_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student who is not enrolled in a tutor receives a 403 Forbidden
    error if they attempt to create a chat with that tutor.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Student A (unenrolled) attempts to create a chat.
    unauthorized_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Unauthorized Chat"},
        headers=context["student_a_headers"],
    )

    assert unauthorized_res.status_code == 403
    assert unauthorized_res.json()["error_code"] == "USER_NOT_ENROLLED"


def test_enrolled_student_cannot_access_another_students_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student, even if enrolled in the same Tutor, cannot access
    the private chat history of another student.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Enroll both students.
    enroll_student(
        client,
        tutor_id,
        STUDENT_A_EMAIL,
        context["teacher_headers"],
        context["student_a_headers"],
    )
    enroll_student(
        client,
        tutor_id,
        STUDENT_B_EMAIL,
        context["teacher_headers"],
        context["student_b_headers"],
    )

    # Student A creates their own private chat.
    chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Student A Chat"},
        headers=context["student_a_headers"],
    )
    chat_id = chat_res.json()["id"]

    # Student B attempts to access Student A's chat messages.
    unauthorized_res = client.get(
        f"{settings.API_ROOT_PATH}/chats/{chat_id}/messages",
        headers=context["student_b_headers"],
    )

    assert unauthorized_res.status_code == 403
    assert unauthorized_res.json()["error_code"] == "CHAT_OWNERSHIP_REQUIRED"


def test_teacher_cannot_post_message_in_students_private_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a teacher cannot post messages into a private chat created by
    one of their students.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    enroll_student(
        client,
        tutor_id,
        STUDENT_A_EMAIL,
        context["teacher_headers"],
        context["student_a_headers"],
    )

    chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Student A's Chat"},
        headers=context["student_a_headers"],
    )
    chat_id = chat_res.json()["id"]

    # The Teacher attempts to post a message.
    unauthorized_res = client.post(
        f"{settings.API_ROOT_PATH}/chats/{chat_id}/query",
        json={"query": "Teacher's message"},
        headers=context["teacher_headers"],
    )

    assert unauthorized_res.status_code == 403
    assert unauthorized_res.json()["error_code"] == "CHAT_OWNERSHIP_REQUIRED"


def test_upload_fails_for_file_exceeding_size_limit(
    client: TestClient,
    db_session: SQLAlchemySession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Tests that the API correctly rejects a file that is larger than the
    configured maximum upload size.
    """
    context = setup_users_and_tutor(client, db_session)
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)

    large_file_content = b"a" * (2 * 1024 * 1024)
    large_file = ("large.pdf", io.BytesIO(large_file_content), "application/pdf")

    response = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}/documents",
        files={"file": large_file},
        headers=context["teacher_headers"],
    )

    assert response.status_code == 413
    assert "File size exceeds the limit of 1 MB" in response.json()["detail"]


def test_upload_succeeds_for_valid_file_within_size_limit(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a valid PDF file under the size limit can be successfully
    uploaded. This test correctly uses the mocked AI services for speed.
    """
    context = setup_users_and_tutor(client, db_session)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "This is a test sentence.")
    pdf_bytes = doc.write()
    doc.close()

    response = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}/documents",
        files={"file": ("valid_doc.pdf", pdf_bytes, "application/pdf")},
        headers=context["teacher_headers"],
    )

    assert response.status_code == 201


def test_teacher_can_update_their_own_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """Tests that a teacher can successfully update a tutor they own."""
    context = setup_users_and_tutor(client, db_session)
    update_payload = {"description": "This is an updated description."}

    response = client.patch(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}",
        json=update_payload,
        headers=context["teacher_headers"],
    )

    assert response.status_code == 200
    assert response.json()["description"] == "This is an updated description."


def test_non_owner_cannot_update_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that an enrolled student cannot update a tutor they do not own.
    """
    context = setup_users_and_tutor(client, db_session)
    enroll_student(
        client,
        context["tutor_id"],
        STUDENT_A_EMAIL,
        context["teacher_headers"],
        context["student_a_headers"],
    )
    update_payload = {"description": "Attempted update by non-owner."}

    response = client.patch(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}",
        json=update_payload,
        headers=context["student_a_headers"],
    )

    assert response.status_code == 403
    assert response.json()["error_code"] == "INSUFFICIENT_PERMISSIONS"


def test_teacher_can_delete_their_own_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """Tests that a teacher can successfully delete a tutor they own."""
    context = setup_users_and_tutor(client, db_session)

    delete_response = client.delete(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}",
        headers=context["teacher_headers"],
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}",
        headers=context["teacher_headers"],
    )
    assert get_response.status_code == 404


def test_teacher_can_remove_student_access(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """Tests that a teacher can fully revoke a student's access to a tutor."""
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    enroll_student(
        client,
        tutor_id,
        STUDENT_A_EMAIL,
        context["teacher_headers"],
        context["student_a_headers"],
    )

    # Verify student can access a resource before removal.
    create_chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Test Chat"},
        headers=context["student_a_headers"],
    )
    assert create_chat_res.status_code == 201

    # Teacher removes the student's access.
    remove_res = client.delete(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/authorized-emails/{STUDENT_A_EMAIL}",
        headers=context["teacher_headers"],
    )
    assert remove_res.status_code == 204

    # Verify student can NO LONGER access the resource.
    create_chat_again_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Another Chat"},
        headers=context["student_a_headers"],
    )
    assert create_chat_again_res.status_code == 403
    assert create_chat_again_res.json()["error_code"] == "USER_NOT_ENROLLED"
