import importlib

from fastapi import APIRouter, FastAPI

from src.core.infrastructure.settings import settings
from src.core.infrastructure.utils import discover_modules, discover_routers


def register_api_routers(app: FastAPI) -> None:
    """Discovers and registers all API routers under the '/api/v1' prefix."""
    api_router = APIRouter(prefix=settings.API_ROOT_PATH)

    for discovered in discover_routers(consumer_area="api"):
        api_router.include_router(discovered.router)
        if discovered.tag_metadata:
            app.openapi_tags = (app.openapi_tags or []) + [discovered.tag_metadata]

    app.include_router(api_router)


def import_models() -> None:
    """
    Dynamically imports all `models` submodules from every API feature module.
    """
    for module in discover_modules("api"):
        try:
            importlib.import_module(f"src.api.{module}.domain.models")
        except ImportError:
            continue  # It's okay if a module doesn't have models
