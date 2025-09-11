import importlib
import pkgutil
from typing import Iterator

from fastapi import APIRouter, FastAPI


def _discover_ui_routers() -> Iterator[APIRouter]:
    """
    A generator that discovers and yields all APIRouter instances from
    the `src/ui/routers/` directory.
    """
    routers_path = "src.ui.routers"
    routers_module = importlib.import_module(routers_path)

    for _, module_name, _ in pkgutil.iter_modules(routers_module.__path__):
        if module_name.endswith("_router"):
            module = importlib.import_module(f"{routers_path}.{module_name}")
            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                yield module.router


def register_ui_routers(app: FastAPI) -> None:
    """
    Discovers all UI routers and registers them with the FastAPI application.
    """
    for router in _discover_ui_routers():
        app.include_router(router)
