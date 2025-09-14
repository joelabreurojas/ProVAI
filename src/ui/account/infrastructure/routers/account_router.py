from fastapi import APIRouter, Depends, Request, Response

from src.ui.shared.infrastructure.dependencies import get_sidebar_context
from src.ui.shared.infrastructure.utils import render_template

router = APIRouter(prefix="/account", tags=["UI - Account"], include_in_schema=False)


@router.get("")
async def serve_account_page(
    request: Request,
    sidebar_context: dict = Depends(get_sidebar_context),
) -> Response:
    """
    Serves the main account management page, inheriting the shared app layout.
    """
    context = {
        "request": request,
        "title": "Your Account",
        "navbar_type": "app",
        **sidebar_context,  # Provides 'user' and 'tutors' for the layout
    }
    return render_template("account.html", context)
