import importlib
import pkgutil
from typing import Iterator, NamedTuple

from fastapi import APIRouter

from src.core.infrastructure.utils import discover_modules


class DiscoveredRouter(NamedTuple):
    router: APIRouter
    tag_metadata: dict[str, str] | None


def discover_routers(consumer_area: str) -> Iterator[DiscoveredRouter]:
    """
    A generic generator that discovers and yields all APIRouter instances
    from a given consumer area (e.g., 'api' or 'ui').
    """
    for module_name in discover_modules(consumer_area):
        try:
            router_module_path = (
                f"src.{consumer_area}.{module_name}.infrastructure.routers"
            )
            router_module = importlib.import_module(router_module_path)

            for _, sub_module_name, _ in pkgutil.iter_modules(router_module.__path__):
                full_module_path = f"{router_module_path}.{sub_module_name}"
                module = importlib.import_module(full_module_path)

                if hasattr(module, "router") and isinstance(module.router, APIRouter):
                    tag = getattr(module, "TAG", None)
                    yield DiscoveredRouter(router=module.router, tag_metadata=tag)

        except (ImportError, AttributeError) as e:
            print(f"Skipping router for module {module_name}: {e}")
