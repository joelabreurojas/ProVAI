from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from src.core.application.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
    UserAlreadyExistsError,
)
from src.core.application.protocols import AuthServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import UserCreate
from src.ui.shared.infrastructure.dependencies import (
    get_optional_current_user_from_cookie,
    validate_csrf_token,
)
from src.ui.shared.infrastructure.utils import render_template

router = APIRouter(
    prefix="/auth", tags=["UI - Authentication"], include_in_schema=False
)


@router.get("/login", response_class=Response)
async def serve_login_page(
    request: Request, user: User | None = Depends(get_optional_current_user_from_cookie)
) -> Response:
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    toast_message = request.session.pop("toast_message", None)
    toast_category = request.session.pop("toast_category", "success")

    context = {
        "request": request,
        "toast_message": toast_message,
        "toast_category": toast_category,
        "title": "Login to ProVAI",
    }
    response: Response = render_template("login.html", context)

    return response


@router.get("/register", response_class=Response)
async def serve_register_page(
    request: Request, user: User | None = Depends(get_optional_current_user_from_cookie)
) -> Response:
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    context = {"request": request, "title": "Create Your Account"}
    response: Response = render_template("register.html", context)

    return response


@router.post("/login")
async def handle_login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthServiceProtocol = Depends(),
    _csrf_token: None = Depends(validate_csrf_token),
) -> Response:
    try:
        user, token = auth_service.authenticate_user(email=email, password=password)
        request.session.update({"user_token": token, "user_role": user.role})
        response = Response()
        response.headers["HX-Redirect"] = "/dashboard"
        return response
    except InvalidCredentialsError as e:
        context = {"request": request, "error_message": e.message}
        return render_template("partials/_login_form.html", context)


@router.post("/register")
async def handle_register_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthServiceProtocol = Depends(),
    _csrf_token: None = Depends(validate_csrf_token),
) -> Response:
    try:
        user_data = UserCreate(name=name, email=email, password=password)

        auth_service.register_user(
            name=user_data.name, email=user_data.email, password=user_data.password
        )

        request.session["toast_message"] = "Registration successful! Please log in."
        request.session["toast_category"] = "success"

        return Response(
            status_code=status.HTTP_200_OK, headers={"HX-Redirect": "/auth/login"}
        )

    except ValidationError as e:
        error_message = e.errors()[0]["msg"]
        context = {"request": request, "error_message": error_message}
        return render_template("partials/_register_form.html", context)

    except (UserAlreadyExistsError, InvalidPasswordError) as e:
        # This catches business logic errors from the service.
        context = {"request": request, "error_message": e.message}
        return render_template("partials/_register_form.html", context)


@router.post("/logout")
async def handle_logout(request: Request) -> Response:
    """
    Clears the user's session cookie and redirects them to the landing page.
    """
    request.session.clear()
    return Response(status_code=200, headers={"HX-Redirect": "/"})


@router.get("/forgot-password", response_class=Response)
async def serve_forgot_password_page(
    request: Request, user: User | None = Depends(get_optional_current_user_from_cookie)
) -> Response:
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    context = {"request": request, "title": "Reset Your Password"}
    response: Response = render_template("forgot-password.html", context)

    return response
