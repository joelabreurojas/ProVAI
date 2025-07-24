from fastapi import FastAPI

from src.core.infrastructure.api import health
from src.core.infrastructure.settings import settings


def create_app() -> FastAPI:
    """Application factory, creating and configuring the FastAPI app."""
    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        license_info=settings.LICENSE_INFO,
        openapi_tags=settings.TAGS_METADATA,
    )

    # Root
    @app.get("/", tags=["Root"])
    async def read_root() -> dict[str, str]:
        """A welcome message to confirm that the API is running."""
        return {"message": f"Welcome to {settings.TITLE} API"}

    # API routers
    app.include_router(health.router)

    return app
