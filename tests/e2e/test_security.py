import time

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.core.infrastructure.limiter import limiter


def test_rate_limiting_on_query_endpoint(
    app_and_client: tuple[FastAPI, TestClient],
) -> None:
    """
    Tests that the rate limiter correctly blocks excessive requests to a
    protected endpoint.
    """
    app, client = app_and_client

    @app.get("/test-rate-limit")
    @limiter.limit("5/second")
    async def _test_rate_limit(request: Request) -> dict[str, str]:
        return {"status": "ok"}

    # Make 5 successful requests
    for _ in range(5):
        response = client.get("/test-rate-limit")
        assert response.status_code == 200

    # The 6th request should fail
    response = client.get("/test-rate-limit")
    assert response.status_code == 429
    assert response.json()["error_code"] == "RATE_LIMIT_EXCEEDED"

    # Wait for the rate limit window to reset (1 second)
    time.sleep(1)

    # The next request should now succeed
    response = client.get("/test-rate-limit")
    assert response.status_code == 200
