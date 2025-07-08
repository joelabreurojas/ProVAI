from fastapi import FastAPI

from src.infrastructure.api import health
from src.infrastructure.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        license_info=settings.LICENSE_INFO,
        openapi_tags=settings.TAGS_METADATA,
    )

    # API routers
    app.include_router(health.router)

    @app.get("/", tags=["Root"])
    async def read_root() -> dict[str, str]:
        """Returns a message welcoming the user to the API."""
        return {"message": f"Welcome to {settings.TITLE} API"}

    return app
