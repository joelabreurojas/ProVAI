from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from src.ui.utils import templates

router = APIRouter(
    prefix="/dashboard", tags=["UI - Dashboard"], include_in_schema=False
)


@router.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the main user dashboard with the application navbar."""

    context = {
        "request": request,
        "navbar_type": "app",
    }

    response: HTMLResponse = templates.TemplateResponse("dashboard.html", context)

    return response
