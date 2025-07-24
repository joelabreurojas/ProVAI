from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.exceptions import ApplicationException
from src.infrastructure.api import health
from src.infrastructure.settings import settings


def create_app() -> FastAPI:
    """Application factory, creating and configuring the FastAPI app."""
    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        license_info=settings.LICENSE_INFO,
        openapi_tags=settings.TAGS_METADATA,
    )

    # Exception handler
    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request, exc: ApplicationException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

    return app

    # Root
    @app.get("/", tags=["Root"])
    async def read_root() -> dict[str, str]:
        """A welcome message to confirm that the API is running."""
        return {"message": f"Welcome to {settings.TITLE} API"}

    # API routers
    app.include_router(health.router)
