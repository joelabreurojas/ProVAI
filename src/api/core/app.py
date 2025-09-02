"""
This file contains the application factory for the ProVAI FastAPI application.

It is the main "Composition Root" of the project, responsible for creating and
configuring the FastAPI app instance, including setting up middleware, exception
handlers, and registering routers.
"""

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.core.application.exceptions import AppException
from src.api.core.infrastructure.handlers import (
    app_exception_handler,
    rate_limit_exception_handler,
)
from src.api.core.infrastructure.limiter import limiter
from src.api.core.infrastructure.logging_config import setup_logging
from src.api.core.infrastructure.middleware import logging_middleware
from src.api.core.infrastructure.settings import settings
from src.api.core.modules import import_models, register_api_routers


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
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)

    register_api_routers(app)

    return app
