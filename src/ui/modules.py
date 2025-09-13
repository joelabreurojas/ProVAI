from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.core.infrastructure.utils import discover_modules, discover_routers


def register_ui_routers(app: FastAPI) -> None:
    """Discovers and registers all UI routers with the FastAPI application."""
    for module_name in discover_modules(consumer_area="ui"):
        for discovered in discover_routers(
            routers_module_path=f"src.ui.{module_name}.infrastructure.routers"
        ):
            app.include_router(discovered.router)


def mount_static_files(app: FastAPI) -> None:
    app.mount(
        "/static",
        StaticFiles(directory="src/ui/shared/infrastructure/static"),
        name="static",
    )


def discover_ui_templates() -> list[str]:
    templates = []

    for module in discover_modules("ui"):
        template_path = Path(f"src/ui/{module}/infrastructure/templates")

        if template_path.exists():
            templates.append(str(template_path))

    return templates


def register_ui_templates(app: FastAPI) -> None:
    for template_folder in discover_ui_templates():
        app.state.templates = Jinja2Templates(directory=template_folder)
