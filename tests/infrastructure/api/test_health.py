from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["api_status"] == "ok"
    assert response_json["db_status"] == "ok"
