import io
from typing import Generator

import fitz
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.infrastructure.settings import settings
from tests.helpers import (
    STUDENT_A_EMAIL,
    STUDENT_B_EMAIL,
    setup_users_and_tutor,
)


def test_student_cannot_create_invitation(
    app: FastAPI, client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a user with the 'student' role receives a 403 Forbidden error
    if they attempt to add an authorized email.
    """
    context = setup_users_and_tutor(client, db_session)

    # Student A (a non-owner) tries to add an email to the whitelist.
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

    # The Teacher invites ONLY Student A.
    client.post(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}/authorized-emails",
        json={"emails": [STUDENT_A_EMAIL]},
        headers=context["teacher_headers"],
    )

    # The Teacher gets the tutor's token.
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}",
        headers=context["teacher_headers"],
    )
    invitation_token = tutor_details_res.json()["token"]

    # Student B (the unauthorized user) tries to use the token.
    enrollment_res = client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_b_headers"],  # Authenticated as the wrong student
    )

    assert enrollment_res.status_code == 403
    assert enrollment_res.json()["error_code"] == "INVITATION_EMAIL_MISMATCH"


def test_student_cannot_upload_document_to_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a user with the 'student' role receives a 403 Forbidden error
    if they attempt to upload a document to a Tutor's knowledge base.
    """
    context = setup_users_and_tutor(client, db_session)

    # Enroll the student so they have access for other actions.
    client.post(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}/authorized-emails",
        json={"emails": [STUDENT_A_EMAIL]},
        headers=context["teacher_headers"],
    )
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}",
        headers=context["teacher_headers"],
    )
    invitation_token = tutor_details_res.json()["token"]
    client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_a_headers"],
    )

    # Create a dummy PDF to upload.
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "This is a test PDF.")
    pdf_bytes = doc.write()
    doc.close()

    upload_res = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}/documents",
        files={"file": ("student_upload.pdf", pdf_bytes, "application/pdf")},
        headers=context["student_a_headers"],  # Authenticated as a student
    )

    assert upload_res.status_code == 403
    error_details = upload_res.json()
    assert error_details["error_code"] == "INSUFFICIENT_PERMISSIONS"


def test_unenrolled_student_cannot_access_chat_history(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student who is not enrolled in a tutor receives a 403 Forbidden
    error if they attempt to access a chat belonging to that tutor.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Student A enrolls and creates a chat.
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
    client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_a_headers"],
    )

    student_a_chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Student A Chat"},
        headers=context["student_a_headers"],
    )
    student_a_chat_id = student_a_chat_res.json()["id"]

    # Student B (unenrolled) attempts to access Student A's chat.
    unauthorized_access_res = client.get(
        f"{settings.API_ROOT_PATH}/chats/{student_a_chat_id}/messages",
        headers=context["student_b_headers"],
    )

    assert unauthorized_access_res.status_code == 403
    assert unauthorized_access_res.json()["error_code"] == "USER_NOT_ENROLLED"


def test_enrolled_student_cannot_access_another_students_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student, even if enrolled in the same Tutor, cannot access
    the private chat history of another student.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Teacher invites BOTH students.
    client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/authorized-emails",
        json={"emails": [STUDENT_A_EMAIL, STUDENT_B_EMAIL]},
        headers=context["teacher_headers"],
    )
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}",
        headers=context["teacher_headers"],
    )
    invitation_token = tutor_details_res.json()["token"]

    # Both students enroll.
    client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_a_headers"],
    )
    client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_b_headers"],
    )

    student_a_chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Student A Private Chat"},
        headers=context["student_a_headers"],
    )
    student_a_chat_id = student_a_chat_res.json()["id"]

    # Student B attempts to access Student A's chat.
    unauthorized_access_res = client.get(
        f"{settings.API_ROOT_PATH}/chats/{student_a_chat_id}/messages",
        headers=context["student_b_headers"],
    )

    assert unauthorized_access_res.status_code == 403
    assert unauthorized_access_res.json()["error_code"] == "CHAT_OWNERSHIP_REQUIRED"


def test_teacher_cannot_post_message_in_students_private_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a teacher cannot post messages into a private chat created by
    one of their students.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Student A enrolls.
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
    client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_a_headers"],
    )

    student_chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Student A's Private Notes"},
        headers=context["student_a_headers"],
    )
    student_chat_id = student_chat_res.json()["id"]

    # The Teacher attempts to post a message into the student's chat.
    unauthorized_post_res = client.post(
        f"{settings.API_ROOT_PATH}/chats/{student_chat_id}/query",
        json={"query": "Teacher's message"},
        headers=context["teacher_headers"],
    )

    assert unauthorized_post_res.status_code == 403
    assert unauthorized_post_res.json()["error_code"] == "CHAT_OWNERSHIP_REQUIRED"


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
    tutor_id = context["tutor_id"]
    teacher_headers = context["teacher_headers"]

    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)

    large_file_content = b"a" * (2 * 1024 * 1024)
    large_file = ("large.pdf", io.BytesIO(large_file_content), "application/pdf")

    response = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/documents",
        files={"file": large_file},
        headers=teacher_headers,
    )
    assert response.status_code == 413
    assert "File size exceeds the limit of 1 MB" in response.json()["detail"]


def test_upload_succeeds_for_valid_file_within_size_limit(
    fresh_ai_services: Generator[None, None, None],
    client: TestClient,
    db_session: SQLAlchemySession,
) -> None:
    """
    Tests that a valid PDF file under the size limit can be successfully
    uploaded and ingested.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]
    teacher_headers = context["teacher_headers"]

    # Create a valid PDF that is large enough to produce chunks
    doc = fitz.open()
    page = doc.new_page()
    long_text = "This is a test sentence for our valid PDF. " * 50
    page.insert_text((50, 72), long_text)
    pdf_bytes = doc.write()
    doc.close()

    valid_file = ("valid_doc.pdf", pdf_bytes, "application/pdf")

    response = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/documents",
        files={"file": valid_file},
        headers=teacher_headers,
    )
    assert response.status_code == 201


def test_teacher_can_update_their_own_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """Tests that a teacher can successfully update a tutor they own."""
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]
    teacher_headers = context["teacher_headers"]

    update_payload = {
        "course_name": "Updated Course Name",
        "description": "This is an updated description.",
    }
    response = client.patch(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}",
        json=update_payload,
        headers=teacher_headers,
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["course_name"] == "Updated Course Name"
    assert response_data["description"] == "This is an updated description."


def test_non_owner_cannot_update_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a user (even another teacher or an enrolled student) cannot
    update a tutor they do not own.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Enroll Student A so they have access, but not ownership
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}",
        headers=context["teacher_headers"],
    )
    invitation_token = tutor_details_res.json()["token"]
    client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/authorized-emails",
        json={"emails": [STUDENT_A_EMAIL]},
        headers=context["teacher_headers"],
    )
    client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_a_headers"],
    )

    update_payload = {"description": "Attempted update by non-owner."}
    response = client.patch(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}",
        json=update_payload,
        headers=context["student_a_headers"],  # Authenticated as Student A
    )

    # The service's verify_user_is_tutor_owner will fail.
    assert response.status_code == 403
    assert (
        response.json()["error_code"] == "INSUFFICIENT_PERMISSIONS"
    )  # Or TUTOR_OWNERSHIP_ERROR depending on service logic order
