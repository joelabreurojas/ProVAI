from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_health_check_succeeds(app_and_client: tuple[FastAPI, TestClient]) -> None:
    """
    Tests that the /health endpoint is working correctly, returning a 200
    status and a JSON response indicating both API and DB are 'ok'.
    """
    _, client = app_and_client
    response = client.get("/health")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["api_status"] == "ok"
    assert response_json["db_status"] == "ok"
