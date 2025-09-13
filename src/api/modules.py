import importlib

from fastapi import APIRouter, FastAPI

from src.core.infrastructure.settings import settings
from src.core.infrastructure.utils import (
    discover_modules,
    discover_routers,
    get_registered_overrides,
    import_and_register,
)


def register_api_routers(app: FastAPI) -> None:
    """Discovers and registers all API routers under the '/api/v1' prefix."""
    api_router = APIRouter(prefix=settings.API_ROOT_PATH)

    for module_name in discover_modules(consumer_area="api"):
        for discovered in discover_routers(
            routers_module_path=f"src.api.{module_name}.infrastructure.routers"
        ):
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


def register_api_dependencies(app: FastAPI) -> None:
    """
    Discovers all modules within the 'api' adapter, imports their dependencies
    to trigger registration, and applies the discovered overrides to the app.
    """
    api_modules = discover_modules(consumer_area="api")
    import_and_register(adapter_name="api", module_names=api_modules)

    overrides = get_registered_overrides()
    for protocol, provider in overrides.items():
        app.dependency_overrides[protocol] = provider
