import re
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.domain.models import User
from src.core.infrastructure.settings import settings

VALID_TEACHER_PASSWORD = "TeacherPassword123!"
VALID_STUDENT_A_PASSWORD = "StudentAPassword123!"
VALID_STUDENT_B_PASSWORD = "StudentBPassword123!"
TEACHER_EMAIL = "security-teacher@e2e.com"
STUDENT_A_EMAIL = "student-a@e2e.com"
STUDENT_B_EMAIL = "student-b@e2e.com"


def get_csrf_token_from_response(response_text: str) -> str:
    """Extracts the CSRF token from a login form's HTML."""
    match = re.search(r'name="csrf_token" value="([^"]+)"', response_text)
    assert match is not None, "CSRF token not found in form HTML"
    return match.group(1)


def setup_users_and_tutor(
    client: TestClient, db_session: SQLAlchemySession
) -> dict[str, Any]:
    """
    Helper function to set up the necessary users and tutor for tests.
    It now correctly uses the API_ROOT_PATH for all API calls.
    """
    api_prefix = settings.API_ROOT_PATH

    res_teacher = client.post(
        f"{api_prefix}/auth/register",
        json={
            "name": "Security Teacher",
            "email": TEACHER_EMAIL,
            "password": VALID_TEACHER_PASSWORD,
        },
    )
    assert res_teacher.status_code == 201, (
        f"Failed to register teacher: {res_teacher.text}"
    )

    res_stud_a = client.post(
        f"{api_prefix}/auth/register",
        json={
            "name": "Student A",
            "email": STUDENT_A_EMAIL,
            "password": VALID_STUDENT_A_PASSWORD,
        },
    )
    assert res_stud_a.status_code == 201, (
        f"Failed to register student A: {res_stud_a.text}"
    )

    res_stud_b = client.post(
        f"{api_prefix}/auth/register",
        json={
            "name": "Student B",
            "email": STUDENT_B_EMAIL,
            "password": VALID_STUDENT_B_PASSWORD,
        },
    )
    assert res_stud_b.status_code == 201, (
        f"Failed to register student B: {res_stud_b.text}"
    )

    # Manually promote the teacher
    teacher_db = db_session.query(User).filter_by(email=TEACHER_EMAIL).first()
    assert teacher_db is not None, "Teacher not found in DB after registration."
    teacher_db.role = "teacher"
    db_session.commit()
    db_session.refresh(teacher_db)

    # Log in all users to get tokens
    teacher_login_res = client.post(
        f"{api_prefix}/auth/token",
        data={"email": TEACHER_EMAIL, "password": VALID_TEACHER_PASSWORD},
    )
    student_a_login_res = client.post(
        f"{api_prefix}/auth/token",
        data={"email": STUDENT_A_EMAIL, "password": VALID_STUDENT_A_PASSWORD},
    )
    student_b_login_res = client.post(
        f"{api_prefix}/auth/token",
        data={"email": STUDENT_B_EMAIL, "password": VALID_STUDENT_B_PASSWORD},
    )

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
        f"{api_prefix}/tutors",
        json={"course_name": "Security Test Course"},
        headers=context["teacher_headers"],
    )
    assert tutor_res.status_code == 201, "Failed to create tutor"
    context["tutor_id"] = tutor_res.json()["id"]

    return context
