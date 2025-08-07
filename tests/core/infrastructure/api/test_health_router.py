from fastapi.testclient import TestClient


def test_health_check_succeeds(client: TestClient) -> None:
    """
    Tests that the /health endpoint is working correctly, returning a 200
    status and a JSON response indicating both API and DB are 'ok'.
    """
    response = client.get("/health")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["api_status"] == "ok"
    assert response_json["db_status"] == "ok"
