from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse

from src.api.auth.application.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from src.api.auth.application.protocols import AuthServiceProtocol
from src.api.auth.dependencies import get_auth_service
from src.api.auth.domain.schemas import UserCreate
from src.ui.utils import templates

router = APIRouter(
    prefix="/auth", tags=["UI - Authentication"], include_in_schema=False
)


@router.get("/login", response_class=HTMLResponse)
async def serve_login_page(request: Request):
    """Serves the dedicated login page."""
    context = {"request": request, "title": "Login"}
    response: HTMLResponse = templates.TemplateResponse("login.html", context)

    return response


@router.get("/register", response_class=HTMLResponse)
async def serve_register_page(request: Request):
    """Serves the dedicated registration page."""
    context = {"request": request, "title": "Register"}
    response: HTMLResponse = templates.TemplateResponse("register.html", context)

    return response


@router.post("/login", response_class=HTMLResponse)
async def handle_login_page(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
) -> Response:
    """Handles the HTMX login form submission."""
    try:
        user, token = auth_service.authenticate_user(email, password)
        request.session.update({"user_token": token, "user_email": user.email})
        response = Response(status_code=200, headers={"HX-Redirect": "/dashboard"})

        return response

    except InvalidCredentialsError:
        context = {"request": request, "error_message": "Invalid email or password."}
        response: Response = templates.TemplateResponse("login.html", context)

        return response


@router.post("/register", response_class=HTMLResponse)
async def handle_register_page(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
) -> Response:
    """Handles the HTMX registration form submission."""
    try:
        user_data = UserCreate(name=name, email=email, password=password)
        auth_service.register_user(user_data)
        response = Response(status_code=200, headers={"HX-Redirect": "/login"})

        return response

    except UserAlreadyExistsError:
        context = {"request": request, "error_message": "This email is already taken."}
        response: Response = templates.TemplateResponse("register.html", context)

        return response


@router.post("/logout", response_class=Response)
async def handle_htmx_logout(request: Request) -> Response:
    request.session.clear()
    response = Response(status_code=200, headers={"HX-Redirect": "/"})

    return response


@router.get("/forgot-password", response_class=HTMLResponse)
async def serve_forgot_password_page(request: Request):
    """Serves the dedicated 'Forgot Password' placeholder page."""
    context = {"request": request, "title": "Forgot Password"}
    response: HTMLResponse = templates.TemplateResponse("forgot-password.html", context)

    return response
