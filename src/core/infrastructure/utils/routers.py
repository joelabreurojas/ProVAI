import importlib
import pkgutil
from typing import Iterator, NamedTuple

from fastapi import APIRouter


class DiscoveredRouter(NamedTuple):
    router: APIRouter
    tag_metadata: dict[str, str] | None


def discover_routers(routers_module_path: str) -> Iterator[DiscoveredRouter]:
    """
    A generic generator that discovers and yields all APIRouter instances
    from the routers module path of a consumer area.
    """
    try:
        routers_module = importlib.import_module(routers_module_path)

        for _, sub_module_name, _ in pkgutil.iter_modules(routers_module.__path__):
            full_module_path = f"{routers_module_path}.{sub_module_name}"
            module = importlib.import_module(full_module_path)

            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                tag = getattr(module, "TAG", None)
                yield DiscoveredRouter(router=module.router, tag_metadata=tag)

    except (ImportError, AttributeError) as e:
        print(f"Skipping router discovery for path '{routers_module_path}': {e}")
