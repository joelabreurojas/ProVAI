from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.ui.utils import TEMPLATE_GLOBALS

router = APIRouter(tags=["UI - Root"], include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def serve_landing_page(request: Request):
    """Serves the main application landing page."""
    templates = request.app.state.templates

    context = {
        "request": request,
        "title": "Welcome to ProVAI",
        "is_authenticated": False,
    }
    context.update(TEMPLATE_GLOBALS)

    response: HTMLResponse = templates.TemplateResponse("landing.html", context)

    return response
