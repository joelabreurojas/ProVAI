from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from src.api.ai.dependencies import get_embedding_service, get_llm_service


def test_lightweight_health_check_succeeds(
    client: TestClient,
) -> None:
    """
    Tests the lightweight /health endpoint. This test does NOT mock the AI
    services, because the endpoint is specifically designed NOT to load them.
    """
    response = client.get("/health")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["api_status"] == "ok"
    assert response_json["db_status"] == "ok"
    assert response_json["vector_store_status"] == "ok"


def test_comprehensive_status_check_succeeds_when_all_ok(
    app: FastAPI, client: TestClient, mocker: MockerFixture
) -> None:
    """
    Tests the /status endpoint, mocking all AI services to simulate a
    perfectly healthy state.
    """
    mock_llm_service = mocker.MagicMock()
    app.dependency_overrides[get_llm_service] = lambda: mock_llm_service

    mock_embedding_service = mocker.MagicMock()
    app.dependency_overrides[get_embedding_service] = lambda: mock_embedding_service

    response = client.get("/status")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["api_status"] == "ok"
    assert response_json["db_status"] == "ok"
    assert response_json["vector_store_status"] == "ok"
    assert response_json["llm_status"] == "ok"
    assert response_json["embedding_model_status"] == "ok"


def test_comprehensive_status_check_reports_error_when_llm_fails(
    app: FastAPI, client: TestClient, mocker: MockerFixture
) -> None:
    """
    Tests that the /status endpoint correctly reports an error when a
    deep dependency like the LLM service fails, while the shallow checks remain ok.
    """

    # Simulate ONLY the LLM service failing
    mock_llm_service = mocker.MagicMock()
    mock_llm_service.get_llm.side_effect = Exception("LLM failed to load")
    app.dependency_overrides[get_llm_service] = lambda: mock_llm_service

    mock_embedding_service = mocker.MagicMock()
    app.dependency_overrides[get_embedding_service] = lambda: mock_embedding_service

    response = client.get("/status")
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["api_status"] == "ok"
    assert response_json["db_status"] == "ok"
    assert response_json["vector_store_status"] == "ok"
    assert "error: LLM failed to load" in response_json["llm_status"]
    assert response_json["embedding_model_status"] == "ok"
