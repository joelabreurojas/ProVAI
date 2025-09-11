"""
This file contains the application factory for the ProVAI FastAPI application.

It is the main "Composition Root" of the project, responsible for creating and
configuring the FastAPI app instance, including setting up middleware, exception
handlers, and registering routers.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded

from src.api.modules import import_models, register_api_routers
from src.core.application.exceptions import AppException
from src.core.infrastructure.handlers import (
    app_exception_handler,
    rate_limit_exception_handler,
)
from src.core.infrastructure.limiter import limiter
from src.core.infrastructure.logging_config import setup_logging
from src.core.infrastructure.middlewares import register_middlewares
from src.core.infrastructure.settings import settings
from src.ui.modules import register_ui_routers


def create_app() -> FastAPI:
    """Application factory, creating and configuring the FastAPI app."""
    setup_logging()

    import_models()

    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        contact=settings.CONTACT,
        license_info=settings.LICENSE_INFO,
    )

    app.state.limiter = limiter
    register_middlewares(app)

    app.mount("/static", StaticFiles(directory="src/ui/static"), name="static")
    app.state.templates = Jinja2Templates(directory="src/ui/templates")

    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)

    register_api_routers(app)
    register_ui_routers(app)

    return app
