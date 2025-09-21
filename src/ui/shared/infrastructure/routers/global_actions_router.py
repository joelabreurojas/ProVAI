from typing import Any

from fastapi import APIRouter, Depends, Form, Request, Response

from src.core.application.exceptions import (
    AppException,
    InsufficientPermissionsError,
)
from src.core.application.protocols import TutorServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import TutorCreate
from src.ui.shared.infrastructure.dependencies import (
    get_current_user_from_cookie,
    get_sidebar_context,
)
from src.ui.shared.infrastructure.utils import render_template

router = APIRouter(
    prefix="/actions", tags=["UI - Global Actions"], include_in_schema=False
)


@router.post("/enroll")
async def handle_enrollment(
    request: Request,
    invitation_token: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Handles a student's request to enroll in a tutor via a token."""
    try:
        tutor_service.enroll_student_from_token(
            token=invitation_token, student_user=user
        )
        request.session["toast_message"] = "Successfully enrolled in new Tutor!"
        request.session["toast_category"] = "success"

        response = Response()
        response.headers["HX-Refresh"] = "true"
        return response
    except AppException as e:
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": e.message,
        }
        return render_template("partials/_toast.html", context)


@router.post("/create-tutor")
async def handle_create_tutor(
    request: Request,
    course_name: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
    sidebar_context: dict[str, Any] = Depends(get_sidebar_context),
) -> Response:
    """Handles a teacher's request to create a new tutor from the sidebar."""
    try:
        tutor_service.create_tutor(TutorCreate(course_name=course_name), teacher=user)
        # Re-fetch the sidebar context to get the updated list of tutors
        fresh_sidebar_context = {
            "user": user,
            "tutors": tutor_service.get_tutors_for_user(user),
        }
        context = {"request": request, **fresh_sidebar_context}
        # Return just the updated sidebar to be swapped in by HTMX
        return render_template("partials/_app_sidebar.html", context)
    except InsufficientPermissionsError:
        # This case is less likely due to the UI hiding the button
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": "Only teachers can create new Tutors.",
        }
        return render_template("partials/_toast.html", context)
