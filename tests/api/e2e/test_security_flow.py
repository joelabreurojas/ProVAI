from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.auth.domain.models import User

VALID_TEACHER_PASSWORD = "TeacherPassword123!"
VALID_STUDENT_A_PASSWORD = "StudentAPassword123!"
VALID_STUDENT_B_PASSWORD = "StudentBPassword123!"
TEACHER_EMAIL = "security-teacher@e2e.com"
STUDENT_A_EMAIL = "student-a@e2e.com"
STUDENT_B_EMAIL = "student-b@e2e.com"


def setup_users_and_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> dict[str, Any]:
    """Helper function to set up the necessary users and tutor for security tests."""
    # Register all users
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Security Teacher",
            "email": TEACHER_EMAIL,
            "password": VALID_TEACHER_PASSWORD,
        },
    )
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Student A",
            "email": STUDENT_A_EMAIL,
            "password": VALID_STUDENT_A_PASSWORD,
        },
    )
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Student B (Unauthorized)",
            "email": STUDENT_B_EMAIL,
            "password": VALID_STUDENT_B_PASSWORD,
        },
    )

    # Manually promote the teacher
    teacher_db = db_session.query(User).filter_by(email=TEACHER_EMAIL).first()
    assert teacher_db is not None
    teacher_db.role = "teacher"
    db_session.commit()
    db_session.refresh(teacher_db)

    # Log in all users to get tokens
    teacher_login_res = client.post(
        "/api/v1/auth/token",
        data={"username": TEACHER_EMAIL, "password": VALID_TEACHER_PASSWORD},
    )
    student_a_login_res = client.post(
        "/api/v1/auth/token",
        data={"username": STUDENT_A_EMAIL, "password": VALID_STUDENT_A_PASSWORD},
    )
    student_b_login_res = client.post(
        "/api/v1/auth/token",
        data={"username": STUDENT_B_EMAIL, "password": VALID_STUDENT_B_PASSWORD},
    )

    # Create and return the context needed for tests
    context = {
        "teacher_headers": {
            "Authorization": f"Bearer {teacher_login_res.json()['access_token']}"
        },
        "student_a_headers": {
            "Authorization": f"Bearer {student_a_login_res.json()['access_token']}"
        },
        "student_b_headers": {
            "Authorization": f"Bearer {student_b_login_res.json()['access_token']}"
        },
    }

    # Teacher creates a tutor
    tutor_res = client.post(
        "/api/v1/tutors",
        json={"course_name": "Security Test Course"},
        headers=context["teacher_headers"],
    )
    context["tutor_id"] = tutor_res.json()["id"]

    return context


def test_student_cannot_create_invitation(
    app_and_client: tuple[FastAPI, TestClient], db_session: SQLAlchemySession
) -> None:
    """
    Tests that a user with the 'student' role receives a 403 Forbidden error
    if they attempt to create an invitation.
    """
    _, client = app_and_client
    context = setup_users_and_tutor(client, db_session)

    # Student A tries to create an invitation for the tutor
    invitation_res = client.post(
        "/api/v1/invitations",
        json={
            "tutor_id": context["tutor_id"],
            "student_emails": ["another@student.com"],
        },
        headers=context["student_a_headers"],  # Authenticated as a student
    )

    assert invitation_res.status_code == 403
    assert invitation_res.json()["error_code"] == "INSUFFICIENT_PERMISSIONS"


def test_unauthorized_student_cannot_use_invitation(
    app_and_client: tuple[FastAPI, TestClient], db_session: SQLAlchemySession
) -> None:
    """
    Tests that a student receives a 403 Forbidden error if they try to enroll
    using an invitation link that was created for a different student's email.
    """
    _, client = app_and_client
    context = setup_users_and_tutor(client, db_session)

    # The Teacher invites Student A
    invitation_res = client.post(
        "/api/v1/invitations",
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
        "/api/v1/enrollments",
        json={"invitation_token": invitation_token},
        headers=context["student_b_headers"],  # Authenticated as the wrong student
    )

    assert enrollment_res.status_code == 403
    assert enrollment_res.json()["error_code"] == "INVITATION_EMAIL_MISMATCH"
