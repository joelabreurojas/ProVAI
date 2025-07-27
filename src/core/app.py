from fastapi import FastAPI

from src.core.exceptions import ApplicationException
from src.core.infrastructure.api.handlers import application_exception_handler
from src.core.infrastructure.settings import settings
from src.core.modules import register_routers


def create_app() -> FastAPI:
    """Application factory, creating and configuring the FastAPI app."""
    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        root_path=settings.API_ROOT_PATH,
        contact=settings.CONTACT,
        license_info=settings.LICENSE_INFO,
    )

    app.add_exception_handler(ApplicationException, application_exception_handler)

    register_routers(app)

    @app.get("/", tags=["Root"])
    async def read_root() -> dict[str, str]:
        """A welcome message to confirm that the API is running."""
        return {"message": f"Welcome to {settings.TITLE} API"}

    return app
