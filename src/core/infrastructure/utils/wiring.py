import importlib
from typing import Any, Callable, Type

# It will store mappings from Protocol -> Concrete Provider Function
_REGISTRY: dict[Type[Any], Callable[..., Any]] = {}


def provides(protocol: Type[Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    A decorator to mark a function as a provider for a specific protocol.
    """

    def decorator(provider_func: Callable[..., Any]) -> Callable[..., Any]:
        _REGISTRY[protocol] = provider_func
        return provider_func

    return decorator


def import_and_register(adapter_name: str, module_names: list[str]) -> None:
    """
    Dynamically imports all `dependencies.py` files from a given list of
    modules within a specific adapter to execute the `@provides` decorators.
    """
    for module_name in module_names:
        try:
            importlib.import_module(
                f"src.{adapter_name}.{module_name}.infrastructure.dependencies"
            )
        except ImportError:
            continue


def get_registered_overrides() -> dict[Type[Any], Callable[..., Any]]:
    """
    Returns the current state of the central registry.
    """
    return _REGISTRY
