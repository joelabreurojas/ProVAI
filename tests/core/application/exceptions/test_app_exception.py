from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.application.exceptions import AppException
from src.core.domain.errors import ErrorCode
from src.core.infrastructure.handlers import app_exception_handler


class _DummyError(AppException):
    """A dummy exception for testing the global handler."""

    status_code = 418  # "I'm a teapot"
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
    message = "This is a test exception."


def test_global_exception_handler_formats_errors_correctly() -> None:
    """
    Tests that the global exception handler correctly catches custom
    AppExceptions and formats them into a standard JSON error response.
    """
    app = FastAPI()
    app.add_exception_handler(AppException, app_exception_handler)

    @app.get("/test-exception")
    async def _raise_exception_endpoint() -> None:
        raise _DummyError()

    client = TestClient(app)
    response = client.get("/test-exception")

    assert response.status_code == 418
    assert response.json() == {
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "This is a test exception.",
    }
