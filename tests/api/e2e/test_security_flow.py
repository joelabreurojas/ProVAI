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
    if they attempt to create an invitation.
    """
    context = setup_users_and_tutor(client, db_session)

    # Student A tries to create an invitation for the tutor
    invitation_res = client.post(
        f"{settings.API_ROOT_PATH}/invitations",
        json={
            "tutor_id": context["tutor_id"],
            "student_emails": ["another@student.com"],
        },
        headers=context["student_a_headers"],  # Authenticated as a student
    )

    assert invitation_res.status_code == 403
    assert invitation_res.json()["error_code"] == "INSUFFICIENT_PERMISSIONS"


def test_unauthorized_student_cannot_use_invitation(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student receives a 403 Forbidden error if they try to enroll
    using an invitation link that was created for a different student's email.
    """
    context = setup_users_and_tutor(client, db_session)

    # The Teacher invites Student A
    invitation_res = client.post(
        f"{settings.API_ROOT_PATH}/invitations",
        json={
            "tutor_id": context["tutor_id"],
            "student_emails": [STUDENT_A_EMAIL],
        },
        headers=context["teacher_headers"],
    )
    assert invitation_res.status_code == 201
    invitation_token = invitation_res.json()["invitation_token"]

    # Student B (the unauthorized user) tries to use Student A's token
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

    # Enroll the student so they have access to the tutor for other actions.
    invitation_res = client.post(
        f"{settings.API_ROOT_PATH}/invitations",
        json={"tutor_id": context["tutor_id"], "student_emails": [STUDENT_A_EMAIL]},
        headers=context["teacher_headers"],
    )
    invitation_token = invitation_res.json()["invitation_token"]
    client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_a_headers"],
    )

    # Create a dummy PDF file in memory to upload.
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "This is a test PDF.")
    pdf_bytes = doc.write()
    doc.close()

    upload_res = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{context['tutor_id']}/documents",
        files={"file": ("student_upload.pdf", pdf_bytes, "application/pdf")},
        headers=context["student_a_headers"],  # <-- Authenticated as a student
    )

    assert upload_res.status_code == 403
    error_details = upload_res.json()
    assert error_details["error_code"] == "INSUFFICIENT_PERMISSIONS"
    assert "You do not have the required role" in error_details["message"]


def test_unenrolled_student_cannot_access_chat_history(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student who is not enrolled in a tutor receives a 403 Forbidden
    error if they attempt to access a chat belonging to that tutor.
    """
    # We have a Teacher, an enrolled Student (A), and an unenrolled Student (B).
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # Student A (the legitimate student) enrolls and creates a chat.
    invitation_res = client.post(
        f"{settings.API_ROOT_PATH}/invitations",
        json={"tutor_id": tutor_id, "student_emails": [STUDENT_A_EMAIL]},
        headers=context["teacher_headers"],
    )
    invitation_token = invitation_res.json()["invitation_token"]
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

    # Student B (the unauthorized user) attempts to access Student A's chat.
    unauthorized_access_res = client.get(
        f"{settings.API_ROOT_PATH}/chats/{student_a_chat_id}/messages",
        headers=context["student_b_headers"],  # <-- Authenticated as Student B
    )

    assert unauthorized_access_res.status_code == 403
    error_details = unauthorized_access_res.json()
    assert error_details["error_code"] == "USER_NOT_ENROLLED"
    assert "You are not enrolled" in error_details["message"]


def test_enrolled_student_cannot_access_another_students_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student, even if enrolled in the same Tutor, cannot access
    the private chat history of another student.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # The Teacher invites BOTH Student A and Student B.
    invitation_res = client.post(
        f"{settings.API_ROOT_PATH}/invitations",
        json={
            "tutor_id": tutor_id,
            "student_emails": [STUDENT_A_EMAIL, STUDENT_B_EMAIL],
        },
        headers=context["teacher_headers"],
    )
    invitation_token = invitation_res.json()["invitation_token"]

    # Both students enroll successfully.
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

    # Student A creates their own private chat.
    student_a_chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Student A Private Chat"},
        headers=context["student_a_headers"],
    )
    student_a_chat_id = student_a_chat_res.json()["id"]

    # Student B, who is a legitimate member of the tutor, attempts to
    # access the specific chat created by Student A.
    unauthorized_access_res = client.get(
        f"{settings.API_ROOT_PATH}/chats/{student_a_chat_id}/messages",
        headers=context["student_b_headers"],  # <-- Authenticated as Student B
    )

    assert unauthorized_access_res.status_code == 403
    error_details = unauthorized_access_res.json()

    assert error_details["error_code"] == "CHAT_OWNERSHIP_REQUIRED"
    assert "You are not the owner of this chat" in error_details["message"]


def test_teacher_cannot_post_message_in_students_private_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a teacher, while being the owner of the parent Tutor, cannot
    post messages into a private chat created by one of their students.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]

    # The student enrolls and creates their own private chat.
    invitation_res = client.post(
        f"{settings.API_ROOT_PATH}/invitations",
        json={"tutor_id": tutor_id, "student_emails": [STUDENT_A_EMAIL]},
        headers=context["teacher_headers"],
    )
    invitation_token = invitation_res.json()["invitation_token"]
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

    # The Teacher, owner of the Tutor, attempts to post a message
    # into the student's specific chat instance.
    unauthorized_post_res = client.post(
        f"{settings.API_ROOT_PATH}/chats/{student_chat_id}/query",
        json={"query": "Teacher's message"},
        headers=context["teacher_headers"],  # <-- Authenticated as the Teacher
    )

    assert unauthorized_post_res.status_code == 403
    error_details = unauthorized_post_res.json()

    assert error_details["error_code"] == "CHAT_OWNERSHIP_REQUIRED"
    assert "You are not the owner of this chat" in error_details["message"]


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
