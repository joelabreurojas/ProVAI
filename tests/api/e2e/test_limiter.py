import time

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.core.infrastructure.limiter import limiter
from src.core.infrastructure.settings import settings


def test_rate_limiting_on_query_endpoint(
    app: FastAPI, client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that the rate limiter correctly blocks excessive requests to a
    protected endpoint.
    """
    monkeypatch.setattr(limiter, "enabled", True)

    @app.get(f"{settings.API_ROOT_PATH}/test-rate-limit")
    @limiter.limit("5/second")
    async def _test_rate_limit(request: Request) -> dict[str, str]:
        return {"status": "ok"}

    # Make 5 successful requests
    for _ in range(5):
        response = client.get(f"{settings.API_ROOT_PATH}/test-rate-limit")
        assert response.status_code == 200

    # The 6th request should fail
    response = client.get(f"{settings.API_ROOT_PATH}/test-rate-limit")
    assert response.status_code == 429
    assert response.json()["error_code"] == "RATE_LIMIT_EXCEEDED"

    # Wait for the rate limit window to reset (1 second)
    time.sleep(1)

    # The next request should now succeed
    response = client.get(f"{settings.API_ROOT_PATH}/test-rate-limit")
    assert response.status_code == 200


def test_rate_limiting_on_auth_token_endpoint(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Tests that the rate limiter correctly blocks brute-force login attempts
    on the /auth/token endpoint.
    """
    monkeypatch.setattr(limiter, "enabled", True)

    # Use a unique email to ensure we don't interfere with other tests
    test_email = f"rate-limit-user-{int(time.time())}@test.com"

    # Make 10 requests, which should be allowed. We expect them to fail
    # authentication (401), but not be rate-limited (429).
    for i in range(10):
        response = client.post(
            f"{settings.API_ROOT_PATH}/auth/token",
            data={"username": test_email, "password": f"wrong-password-{i}"},
        )
        assert response.status_code == 401  # Unauthorized, not rate-limited

    # The 11th request within the same minute should be blocked.
    response = client.post(
        f"{settings.API_ROOT_PATH}/auth/token",
        data={"username": test_email, "password": "wrong-password-11"},
    )
    assert response.status_code == 429
    assert response.json()["error_code"] == "RATE_LIMIT_EXCEEDED"
