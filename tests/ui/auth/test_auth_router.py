from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.infrastructure.settings import settings
from tests.helpers import get_csrf_token_from_response


def test_unauthenticated_user_is_redirected_from_dashboard(client: TestClient) -> None:
    """
    Tests that the AuthRedirectMiddleware correctly redirects an unauthenticated
    user from a protected page to the login page.
    """

    # We use follow_redirects=True to simulate what a browser does.
    response = client.get("/dashboard", follow_redirects=True)

    assert response.status_code == 200
    assert "Welcome Back" in response.text
    assert response.url.path == "/auth/login"


def test_full_ui_login_and_redirect_flow(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests the complete UI flow: user logs in and can then access the dashboard.
    """
    # Create the user.
    client.post(
        f"{settings.API_ROOT_PATH}/auth/register",
        json={
            "name": "UI Test User",
            "email": "ui-login@test.com",
            "password": "ValidPassword123!",
        },
    )

    get_response = client.get("/auth/login")
    assert get_response.status_code == 200
    csrf_token = get_csrf_token_from_response(get_response.text)

    # Log in via the UI endpoint.
    login_response = client.post(
        "/auth/login",
        data={
            "username": "ui-login@test.com",
            "password": "ValidPassword123!",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,  # We want to inspect the redirect itself
    )

    assert login_response.status_code == 200
    assert login_response.headers["hx-redirect"] == "/dashboard"

    # Manually set the cookie for the next request
    session_cookie = login_response.cookies.get("session")
    assert session_cookie is not None, "Session cookie was not set after login."
    client.cookies.set("session", session_cookie)

    dashboard_response = client.get("/dashboard")
    assert dashboard_response.status_code == 200


def test_ui_registration_flow(client: TestClient) -> None:
    """
    Tests that a user can successfully register via the UI form endpoint
    and is correctly redirected to the login page with a success message.
    """
    new_user_data = {
        "name": "New UI User",
        "email": "new-ui-user@test.com",
        "password": "ValidPassword123!",
    }

    get_response = client.get("/auth/register")
    assert get_response.status_code == 200
    csrf_token = get_csrf_token_from_response(get_response.text)

    new_user_data["csrf_token"] = csrf_token

    # We use the `data` parameter for form submissions.
    register_response = client.post(
        "/auth/register",
        data=new_user_data,
    )

    assert register_response.status_code == 200
    assert register_response.headers["hx-redirect"] == "/auth/login"

    assert "session" in client.cookies
    assert "user_token" not in client.cookies

    login_page_response = client.get(register_response.headers["hx-redirect"])

    assert login_page_response.status_code == 200
    assert "Registration successful!" in login_page_response.text
