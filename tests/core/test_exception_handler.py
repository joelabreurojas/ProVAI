from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.core.errors import ErrorCode
from src.core.exceptions import ApplicationException
from src.core.infrastructure.api.handlers import application_exception_handler


class DummyError(ApplicationException):
    status_code = 418  # "I'm a teapot"
    error_code = ErrorCode.INTERNAL_SERVER_ERROR  # Default for the test
    message = "This is a test exception."


def test_global_exception_handler() -> None:
    app = FastAPI()

    app.add_exception_handler(ApplicationException, application_exception_handler)

    @app.get("/test-exception")
    async def raise_exception_endpoint() -> JSONResponse:
        raise DummyError()

    client = TestClient(app)
    response = client.get("/test-exception")

    assert response.status_code == 418
    assert response.json()["message"] == "This is a test exception."
