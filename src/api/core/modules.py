"""
This file acts as the central registry for all modules in the ProVAI
application.

By defining all modules in one place, we can programmatically discover
and wire up their components (routers, models, etc.) without having
to manually update multiple files every time a new feature is added.
"""

import importlib
import pkgutil
from typing import Iterator, NamedTuple

from fastapi import APIRouter, FastAPI

from src.api.core.constants import PROJECT_ROOT


def _discover_app_modules() -> list[str]:
    """
    Discovers all valid feature modules in the `src` directory.
    A directory is considered a module if it's a Python package.
    """
    src_path = PROJECT_ROOT / "src/api"

    return [
        d.name
        for d in src_path.iterdir()
        if d.is_dir() and (d / "__init__.py").exists()
    ]


APPLICATION_MODULES = _discover_app_modules()


class _DiscoveredRouter(NamedTuple):
    router: APIRouter
    tag_metadata: dict[str, str] | None


def _discover_routers() -> Iterator[_DiscoveredRouter]:
    """
    A generator that discovers and yields all APIRouter instances from
    the modules declared in APPLICATION_MODULES.
    """
    for module_name in APPLICATION_MODULES:
        api_path = f"src.api.{module_name}.infrastructure.routers"

        try:
            api_module_path = importlib.import_module(api_path).__path__

            # Scan all files in the api directory of the module
            for _, sub_module_name, _ in pkgutil.iter_modules(api_module_path):
                if sub_module_name.endswith("_router"):
                    router_path = f"{api_path}.{sub_module_name}"
                    router_module = importlib.import_module(router_path)

                    yield _DiscoveredRouter(
                        router=router_module.router,
                        tag_metadata=getattr(router_module, "TAG", None),
                    )

        except (ImportError, AttributeError) as e:
            print(f"Skipping router for module {module_name}: {e}")


def register_routers(app: FastAPI) -> None:
    """
    Discovers all routers and registers them with the FastAPI application,
    including their OpenAPI tags.
    """
    all_tags = [{"name": "Root", "description": "Root-level endpoints."}]

    for discovered in _discover_routers():
        app.include_router(discovered.router)

        if discovered.tag_metadata:
            all_tags.append(discovered.tag_metadata)

    app.openapi_tags = all_tags


def import_models() -> None:
    """
    Dynamically imports all `models.py` files from every feature module.
    This is used by Alembic to ensure all tables are discoverable.
    The function doesn't need to return anything; the act of importing
    is what makes the models available to SQLAlchemy's Base.
    """
    for module_name in APPLICATION_MODULES:
        try:
            importlib.import_module(f"src.api.{module_name}.domain.models")
        except ImportError:
            continue  # It's okay if a module doesn't have models
