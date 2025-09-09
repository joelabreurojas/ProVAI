from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from src.ui.utils import templates

router = APIRouter(tags=["UI - Root"], include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def serve_landing_page(request: Request) -> HTMLResponse:
    """Serves the main application landing page."""

    context = {
        "request": request,
        "title": "Welcome to ProVAI",
        "navbar_type": "public",
    }

    response: HTMLResponse = templates.TemplateResponse("landing.html", context)

    return response
