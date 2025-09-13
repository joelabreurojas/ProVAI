import importlib
import pkgutil


def import_core_models() -> None:
    """
    Dynamically imports all `models` submodules from the core domain.

    This is essential for tools like Alembic that need to discover all
    SQLAlchemy models to correctly manage the database schema.
    """
    core_models_path = "src.core.domain.models"

    module = importlib.import_module(core_models_path)

    for _, module_name, _ in pkgutil.iter_modules(module.__path__):
        try:
            full_module_path = f"{core_models_path}.{module_name}"
            importlib.import_module(full_module_path)
        except ImportError as e:
            print(f"Could not import model submodule: {full_module_path}. Error: {e}")
