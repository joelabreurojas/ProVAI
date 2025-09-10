from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from src.api.auth.application.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
    UserAlreadyExistsError,
)
from src.api.auth.application.protocols import AuthServiceProtocol
from src.api.auth.dependencies import get_auth_service
from src.api.auth.domain.models import User
from src.ui.dependencies import get_optional_current_user_from_cookie
from src.ui.utils import templates

router = APIRouter(
    prefix="/auth", tags=["UI - Authentication"], include_in_schema=False
)


@router.get("/login", response_class=HTMLResponse)
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
    response: HTMLResponse = templates.TemplateResponse("login.html", context)
    return response


@router.get("/register", response_class=HTMLResponse)
async def serve_register_page(
    request: Request, user: User | None = Depends(get_optional_current_user_from_cookie)
) -> Response:
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    context = {"request": request, "title": "Create Your Account"}
    response: HTMLResponse = templates.TemplateResponse("register.html", context)
    return response


@router.post("/login")
async def handle_login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
) -> Response:
    try:
        user, token = auth_service.authenticate_user(email, password)
        request.session.update({"user_token": token, "user_role": user.role})

        return Response(
            status_code=status.HTTP_200_OK, headers={"HX-Redirect": "/dashboard"}
        )

    except InvalidCredentialsError:
        context = {"request": request, "error_message": "Invalid email or password."}

        response: HTMLResponse = templates.TemplateResponse(
            "partials/_login_form.html", context
        )
        return response


@router.post("/register")
async def handle_register_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
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
        return templates.TemplateResponse("partials/_register_form.html", context)


@router.post("/logout")
async def handle_logout(request: Request) -> Response:
    """
    Clears the user's session cookie and redirects them to the landing page.
    """
    request.session.clear()
    response = Response(status_code=200, headers={"HX-Redirect": "/"})

    return response


@router.get("/forgot-password", response_class=HTMLResponse)
async def serve_forgot_password_page(
    request: Request, user: User | None = Depends(get_optional_current_user_from_cookie)
) -> Response:
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    context = {"request": request, "title": "Reset Your Password"}
    response: HTMLResponse = templates.TemplateResponse("forgot-password.html", context)
    return response
