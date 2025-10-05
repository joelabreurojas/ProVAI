from fastapi.testclient import TestClient

from tests.helpers import get_csrf_token_from_response


def test_form_submission_fails_without_csrf_token(client: TestClient) -> None:
    """
    Tests that a POST request to a protected form endpoint fails with a 422
    error if the CSRF token form field is missing.
    """
    response = client.post(
        "/auth/login",
        data={"email": "test@test.com", "password": "password"},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Field required"}


def test_form_submission_succeeds_with_valid_csrf_token(client: TestClient) -> None:
    """
    Tests that a POST request with a valid, session-matched CSRF token
    passes the validation dependency.
    """
    get_response = client.get("/auth/login")
    assert get_response.status_code == 200

    # The server has now set a CSRF token in the session cookie, and our
    # client will automatically manage this cookie for subsequent requests.

    csrf_token = get_csrf_token_from_response(get_response.text)
    assert csrf_token is not None, "CSRF token not found in the login form."

    post_response = client.post(
        "/auth/login",
        data={
            "email": "no-such-user@test.com",
            "password": "password",
            "csrf_token": csrf_token,
        },
    )

    # As long as the status code is NOT 403 Forbidden, we know the CSRF check passed.
    assert post_response.status_code == 200
    assert "Incorrect email or password" in post_response.text
