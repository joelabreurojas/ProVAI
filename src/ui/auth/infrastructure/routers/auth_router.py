from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.core.application.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
    UserAlreadyExistsError,
)
from src.core.application.protocols import AuthServiceProtocol
from src.core.domain.models import User
from src.ui.shared.infrastructure.dependencies import (
    get_optional_current_user_from_cookie,
)
from src.ui.shared.infrastructure.utils import render_template

router = APIRouter(
    prefix="/auth", tags=["UI - Authentication"], include_in_schema=False
)


@router.get("/login", response_class=Response, name="serve_login_page")
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
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceProtocol = Depends(),
) -> Response:
    try:
        user, token = auth_service.authenticate_user(
            email=form_data.username, password=form_data.password
        )

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
) -> Response:
    try:
        auth_service.register_user(name=name, email=email, password=password)

        request.session["toast_message"] = "Registration successful!"
        request.session["toast_category"] = "success"

        return Response(
            status_code=status.HTTP_200_OK, headers={"HX-Redirect": "/auth/login"}
        )

    except (UserAlreadyExistsError, InvalidPasswordError) as e:
        context = {"request": request, "error_message": e.message}
        response: Response = render_template("partials/_register_form.html", context)

        return response


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
