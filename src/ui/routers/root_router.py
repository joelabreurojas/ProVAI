from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI Root"], include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def show_landing_page(request: Request) -> HTMLResponse:
    """Serves the main application landing page."""
    templates = request.app.state.templates

    response: HTMLResponse = templates.TemplateResponse(
        "landing.html", {"request": request, "is_authenticated": False}
    )

    return response
