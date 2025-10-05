import json
from typing import Any

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.core.application.exceptions import AppException
from src.core.application.protocols import TutorServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import TutorCreate
from src.ui.shared.infrastructure.dependencies import (
    get_current_user_from_cookie,
    get_sidebar_context,
    validate_csrf_token,
)
from src.ui.shared.infrastructure.utils import htmx_trigger, render_template

router = APIRouter(prefix="/actions", tags=["UI - Global Actions"])


@router.post("/create-tutor")
async def handle_create_tutor(
    request: Request,
    course_name: str = Form(...),
    view: str = Form("assistants"),
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """Handles a teacher's request to create a new tutor from the modal."""
    try:
        tutor_data = TutorCreate(course_name=course_name)

        tutor_service.create_tutor(tutor_create=tutor_data, teacher=user)

        context = {
            "request": request,
            "toast_category": "success",
            "toast_message": "Assistant created successfully!",
        }
        response = render_template("partials/_toast.html", context)
        events = {"closeModals": "true", "refreshTutorList": "true"}
        return htmx_trigger(response, events=events, request=request)

    except ValidationError as e:
        error_message = e.errors()[0]["msg"].removeprefix("Value error, ")
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": error_message,
        }
        response = render_template("partials/_toast.html", context)
        return htmx_trigger(response, events={}, request=request)

    except AppException as e:
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": e.message,
        }
        response = render_template("partials/_toast.html", context)
        return htmx_trigger(response, events={}, request=request)


@router.post("/enroll")
async def handle_enrollment(
    request: Request,
    token: str = Form(...),
    view: str = Form("tutors"),
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Handles a student's request to enroll in a new tutor from the modal."""
    try:
        tutor_service.enroll_student_from_token(token=token, student_user=user)

        context = {
            "request": request,
            "toast_category": "success",
            "toast_message": "Successfully enrolled!",
        }
        response = render_template("partials/_toast.html", context)

        events = {"closeModals": "true", "refreshTutorList": "true"}
        return htmx_trigger(response, events=events, request=request)

    except AppException as e:
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": e.message,
        }
        response = render_template("partials/_toast.html", context)
        return htmx_trigger(response, events={}, request=request)


@router.get("/sidebar")
async def get_sidebar_partial(
    request: Request,
    sidebar_context: dict[str, Any] = Depends(get_sidebar_context),
) -> Response:
    """Endpoint that returns only the rendered app sidebar partial."""
    final_context = sidebar_context.copy()
    final_context["request"] = request
    return render_template("partials/_app_sidebar.html", final_context)


@router.get("/tutors-data", response_class=JSONResponse)
async def get_tutors_as_json(
    sidebar_context: dict[str, Any] = Depends(get_sidebar_context),
) -> JSONResponse:
    """
    Returns the user's full list of tutors (both owned and enrolled) as a
    clean JSON array.
    """
    return JSONResponse(content=json.loads(sidebar_context["tutors_json"]))


@router.get("/error-toast")
async def get_error_toast(request: Request) -> Response:
    """
    An endpoint that simply returns a generic error toast partial.
    Useful for triggering from client-side scripts on unexpected failures.
    """
    context = {
        "request": request,
        "toast_category": "error",
        "toast_message": "An unexpected error occurred. Please reload the page.",
    }
    return render_template("partials/_toast.html", context)
