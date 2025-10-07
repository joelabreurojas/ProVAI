from typing import Any

from fastapi import APIRouter, Depends, Request, Response

from src.ui.shared.infrastructure.dependencies import get_sidebar_context
from src.ui.shared.infrastructure.utils import render_template

router = APIRouter(
    prefix="/dashboard", tags=["UI - Dashboard"], include_in_schema=False
)


@router.get("")
async def serve_dashboard(
    request: Request,
    sidebar_context: dict[str, Any] = Depends(get_sidebar_context),
) -> Response:
    """
    Serves the main dashboard page for the authenticated user.
    """
    toast_message = request.session.pop("toast_message", None)
    toast_category = request.session.pop("toast_category", "success")

    context = {
        "request": request,
        "navbar_type": "app",
        "title": "Your Learning Hub",
        "toast_message": toast_message,
        "toast_category": toast_category,
        **sidebar_context,
    }
    response: Response = render_template("dashboard.html", context)
    return response
