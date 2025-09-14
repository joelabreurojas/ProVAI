import time

from fastapi import APIRouter, Depends, Form, Request, Response

from src.core.application.exceptions import InsufficientPermissionsError
from src.core.application.protocols import TutorServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import TutorCreate
from src.ui.shared.infrastructure.dependencies import (
    get_current_user_from_cookie,
    get_sidebar_context,
)
from src.ui.shared.infrastructure.utils import render_template

router = APIRouter(
    prefix="/dashboard", tags=["UI - Dashboard"], include_in_schema=False
)


@router.get("")
async def serve_dashboard(
    request: Request,
    sidebar_context: dict = Depends(get_sidebar_context),
) -> Response:
    """
    Serves the main dashboard page for the authenticated user.
    """
    context = {
        "request": request,
        "navbar_type": "app",
        "title": "Your Learning Hub",
        **sidebar_context,
    }

    response: Response = render_template("dashboard.html", context)

    return response


@router.get("/tutors", response_class=Response)
async def serve_tutor_list(
    request: Request,
    sidebar_context: dict = Depends(get_sidebar_context),
) -> Response:
    """
    Fetches the list of tutors for the current user and renders them
    as an HTML partial. This is intended for HTMX swaps.
    """
    context = {"request": request, **sidebar_context}
    response: Response = render_template("partials/_app_sidebar.html", context)
    return response


@router.post("/tutors", response_class=Response)
async def handle_create_tutor(
    request: Request,
    course_name: str = Form(...),
    # We still need the raw user object for the service call
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Handles creating a new Tutor via HTMX with professional error handling."""
    try:
        tutor_service.create_tutor(TutorCreate(course_name=course_name), teacher=user)

        # After creation, fetch the fresh context to re-render the sidebar
        fresh_sidebar_context = {
            "user": user,
            "tutors": tutor_service.get_tutors_for_user(user),
        }
        context = {"request": request, **fresh_sidebar_context}

        response: Response = render_template("partials/_app_sidebar.html", context)
        # Use HX-Trigger to also send an event that other parts of the UI can listen to
        response.headers["HX-Trigger"] = "tutorListChanged"
        return response

    except InsufficientPermissionsError:
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": "Only teachers can create new Tutors.",
        }
        # This will render the toast and swap it into the body
        response = render_template("partials/_toast.html", context)
        return response
