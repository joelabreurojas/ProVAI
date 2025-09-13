from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from src.api.modules import (
    register_api_dependencies,
    register_api_routers,
)
from src.core.application.exceptions import AppException
from src.core.infrastructure.handlers import (
    app_exception_handler,
    rate_limit_exception_handler,
)
from src.core.infrastructure.limiter import limiter
from src.core.infrastructure.logging_config import setup_logging
from src.core.infrastructure.middlewares import register_middlewares
from src.core.infrastructure.settings import settings
from src.core.infrastructure.utils import import_core_models
from src.ui.modules import (
    mount_static_files,
    register_ui_routers,
    register_ui_templates,
)
from src.ui.shared.infrastructure.middlewares import AuthRedirectMiddleware


def create_app() -> FastAPI:
    """Application factory, creating and configuring the FastAPI app."""
    setup_logging()

    import_core_models()

    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        contact=settings.CONTACT,
        license_info=settings.LICENSE_INFO,
    )

    register_api_dependencies(app)

    app.state.limiter = limiter
    register_middlewares(app, extra=[(AuthRedirectMiddleware, {})])

    mount_static_files(app)
    register_ui_templates(app)

    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)

    register_api_routers(app)
    register_ui_routers(app)

    return app
