import time

from fastapi import APIRouter, Depends, Form, Request, Response

from src.api.auth.application.exceptions import InsufficientPermissionsError
from src.api.auth.domain.models import User
from src.api.tutor.application.protocols import TutorServiceProtocol
from src.api.tutor.dependencies import get_tutor_service
from src.api.tutor.domain.schemas import TutorCreate
from src.ui.dependencies import get_current_user_from_cookie
from src.ui.utils import render_template

router = APIRouter(
    prefix="/dashboard", tags=["UI - Dashboard"], include_in_schema=False
)


@router.get("/")
async def serve_dashboard(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> Response:
    tutors = tutor_service.get_tutors_for_user(user)

    context = {
        "request": request,
        "navbar_type": "app",
        "user": user,
        "tutors": tutors,
        "title": "Your Learning Hub",
    }

    return render_template("dashboard.html", context)


@router.get("/tutors", response_class=Response)
async def serve_tutor_list(
    request: Request,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> Response:
    """
    Fetches the list of tutors for the current user and renders them
    as an HTML partial. This is called by HTMX.
    """
    tutors = tutor_service.get_tutors_for_user(user)
    context = {"request": request, "tutors": tutors, "user": user}

    return render_template("partials/_tutor_list.html", context)


@router.post("/tutors", response_class=Response)
async def handle_create_tutor(
    request: Request,
    course_name: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(get_tutor_service),
) -> Response:
    """Handles creating a new Tutor via HTMX with professional error handling."""
    try:
        tutor_service.create_tutor(TutorCreate(course_name=course_name), teacher=user)

        tutors = tutor_service.get_tutors_for_user(user)
        context = {"request": request, "tutors": tutors, "user": user}

        return render_template("partials/_tutor_list.html", context)

    except InsufficientPermissionsError:
        context = {
            "request": request,
            "toast_id": f"toast-error-{int(time.time())}",
            "toast_type": "error",
            "title": "Authorization Error",
            "message": "Only teachers can create new Tutors.",
        }

        return render_template(
            "partials/_toast.html",
            context,
            headers={"HX-Reswap": "beforeend", "HX-Retarget": "#toast-container"},
        )
