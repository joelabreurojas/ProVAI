from fastapi import APIRouter, Depends, Request, Response, status
from starlette.responses import HTMLResponse, RedirectResponse

from src.api.auth.domain.models import User
from src.ui.dependencies import get_optional_current_user_from_cookie
from src.ui.utils import templates

router = APIRouter(tags=["UI - Root"], include_in_schema=False)


@router.get("/")
async def serve_landing_page(
    request: Request,
    user: User | None = Depends(get_optional_current_user_from_cookie),
) -> Response:
    """
    Serves the main landing page. If the user is already logged in, it
    redirects them straight to their dashboard.
    """
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    context = {
        "request": request,
        "navbar_type": "public",
        "title": "Welcome to ProVAI",
    }
    response: HTMLResponse = templates.TemplateResponse("landing.html", context)
    return response
