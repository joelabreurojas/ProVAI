from src.core.infrastructure.constants import PROJECT_ROOT


def discover_modules(consumer_area: str) -> list[str]:
    """
    Discovers all valid feature modules within a given top-level consumer area.
    e.g., consumer_area = "api" or "ui"
    """
    area_path = PROJECT_ROOT / "src" / consumer_area
    if not area_path.is_dir():
        return []

    return [
        d.name
        for d in area_path.iterdir()
        if d.is_dir() and (d / "__init__.py").exists()
    ]
