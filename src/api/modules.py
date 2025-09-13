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
        router_path = f"src.api.{module_name}.infrastructure.routers"
        for discovered in discover_routers(routers_module_path=router_path):
            api_router.include_router(discovered.router)
            if discovered.tag_metadata:
                if app.openapi_tags is None:
                    app.openapi_tags = []
                app.openapi_tags.append(discovered.tag_metadata)

    app.include_router(api_router)


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
