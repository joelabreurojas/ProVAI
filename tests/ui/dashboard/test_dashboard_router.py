from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLAlchemySession

# Import the helper from the e2e tests to create users easily
from tests.helpers import (
    TEACHER_EMAIL,
    VALID_TEACHER_PASSWORD,
    get_csrf_token_from_response,
    setup_users_and_tutor,
)


def test_teacher_can_view_and_create_tutor_on_dashboard(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a logged-in teacher can view their dashboard and successfully
    create a new Tutor via the HTMX form.
    """
    setup_users_and_tutor(client, db_session)

    get_login_response = client.get("/auth/login")
    csrf_token_login = get_csrf_token_from_response(get_login_response.text)

    # Simulate the teacher logging in via the UI form.
    login_response = client.post(
        "/auth/login",
        data={
            "username": TEACHER_EMAIL,
            "password": VALID_TEACHER_PASSWORD,
            "csrf_token": csrf_token_login,
        },
    )

    session_cookie = login_response.cookies.get("session")
    assert session_cookie is not None, "Session cookie was not set after login."
    client.cookies.set("session", session_cookie)

    # Access the dashboard
    dashboard_response = client.get("/dashboard")
    assert dashboard_response.status_code == 200
    csrf_token_dashboard = get_csrf_token_from_response(dashboard_response.text)

    assert dashboard_response.status_code == 200
    assert "Your Learning Hub" in dashboard_response.text
    # Check that the initial tutor created by the helper is visible.
    assert "Security Test Course" in dashboard_response.text
    # Check that the form for creating a new tutor is visible for the teacher.
    assert "Create New Tutor" in dashboard_response.text

    # The teacher submits the "Create New Tutor" form via the HTMX endpoint.
    create_tutor_response = client.post(
        "/dashboard/tutors",
        data={
            "course_name": "New HTMX Course",
            "csrf_token": csrf_token_dashboard,
        },
    )

    # The response is a 200 OK containing the updated HTML partial,
    # which now includes both the new and old tutors.
    assert create_tutor_response.status_code == 200
    assert "New HTMX Course" in create_tutor_response.text
    assert "Security Test Course" in create_tutor_response.text
