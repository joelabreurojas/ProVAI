"""
This file acts as the central registry for all API modules in the ProVAI
application.

It programmatically discovers and wires up their components, specifically the API
routers, ensuring that all machine-readable endpoints are consistently prefixed
and documented.
"""

import importlib
import pkgutil
from typing import Iterator, NamedTuple

from fastapi import APIRouter, FastAPI

from src.api.core.constants import PROJECT_ROOT
from src.api.core.infrastructure.settings import settings


def _discover_api_modules() -> list[str]:
    """
    Discovers all valid feature modules ONLY within the `src/api` directory.
    """
    api_path = PROJECT_ROOT / "src" / "api"

    return [
        d.name
        for d in api_path.iterdir()
        if d.is_dir() and (d / "__init__.py").exists()
    ]


API_MODULES = _discover_api_modules()


class _DiscoveredRouter(NamedTuple):
    router: APIRouter
    tag_metadata: dict[str, str] | None


def _discover_api_routers() -> Iterator[_DiscoveredRouter]:
    """
    A generator that discovers and yields all APIRouter instances from
    the modules declared in APPLICATION_MODULES.
    """
    for module_name in API_MODULES:
        api_path = f"src.api.{module_name}.infrastructure.routers"

        try:
            api_module_path = importlib.import_module(api_path).__path__

            # Scan all files in the api directory of the module
            for _, sub_module_name, _ in pkgutil.iter_modules(api_module_path):
                if sub_module_name.endswith("_router"):
                    router_path = f"{api_path}.{sub_module_name}"
                    router_module = importlib.import_module(router_path)

                    if hasattr(router_module, "router"):
                        yield _DiscoveredRouter(
                            router=router_module.router,
                            tag_metadata=getattr(router_module, "TAG", None),
                        )

        except (ImportError, AttributeError) as e:
            print(f"Skipping router for module {module_name}: {e}")


def register_api_routers(app: FastAPI) -> None:
    """
    Discovers all API routers and registers them under a master router,
    applying the global API prefix from settings.
    """
    all_tags = app.openapi_tags or []
    api_router = APIRouter(prefix=settings.API_ROOT_PATH)

    for discovered in _discover_api_routers():
        api_router.include_router(discovered.router)
        if discovered.tag_metadata and discovered.tag_metadata not in all_tags:
            all_tags.append(discovered.tag_metadata)

    app.include_router(api_router)
    app.openapi_tags = all_tags


def import_models() -> None:
    """
    Dynamically imports all `models` submodules from every API feature module.
    """
    for module_name in API_MODULES:
        try:
            importlib.import_module(f"src.api.{module_name}.domain.models")
        except ImportError:
            continue  # It's okay if a module doesn't have models
