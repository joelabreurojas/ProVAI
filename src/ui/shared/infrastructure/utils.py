import datetime
from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from src.ui.modules import discover_ui_templates
from src.ui.shared.infrastructure.security import csrf_service

templates = Jinja2Templates(directory=discover_ui_templates())


def global_context(request: Request) -> dict[str, Any]:
    """
    Returns a dictionary of global variables to be available in all templates.
    """
    return {
        "now": datetime.datetime.now(datetime.UTC),
        # We can add any other global variables here in the future
        # e.g., "current_user": get_optional_current_user_from_cookie(request)
    }


def render_template(
    name: str,
    context: dict[str, Any],
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> _TemplateResponse:
    """
    A helper function to render a Jinja2 template with our global context.
    This is the definitive and ONLY way templates should be rendered.
    """
    request = context["request"]

    full_context = global_context(request)
    full_context.update(context)

    # Generate/retrieve the CSRF token and add it to the context for the template.
    if "csrf_token" not in full_context:
        if "csrf_token" not in request.session:
            request.session["csrf_token"] = csrf_service.generate_token()
        full_context["csrf_token"] = request.session["csrf_token"]

    return templates.TemplateResponse(
        request, name, full_context, status_code=status_code, headers=headers
    )
