import httpx
from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse

from src.core.domain.models import User
from src.core.infrastructure.settings import settings
from src.ui.shared.infrastructure.dependencies import (
    get_authenticated_bff_api_client,
    get_optional_current_user_from_cookie,
    get_unauthenticated_bff_api_client,
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
    _csrf_token: None = Depends(validate_csrf_token),
    unauthenticated_client_manager: httpx.AsyncClient = Depends(
        get_unauthenticated_bff_api_client
    ),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
) -> Response:
    # Use 'async with' to get the actual client from the context manager
    async with unauthenticated_client_manager as client:
        api_response = await client.post(
            "/auth/token", data={"email": email, "password": password}
        )

    if api_response.status_code != status.HTTP_200_OK:
        error_message = api_response.json().get(
            "detail", "Incorrect email or password."
        )
        context = {"request": request, "error_message": error_message}
        return render_template("partials/_login_form.html", context)

    token_data = api_response.json()
    token = token_data.get("access_token")

    # This is a temporary measure to update the session for the next dependency
    request.session["user_token"] = token

    # Use the dependency-injected authenticated client to fetch the user profile
    async with authenticated_client_manager as authenticated_client:
        me_response = await authenticated_client.get("/users/me")

    if me_response.status_code != status.HTTP_200_OK:
        context = {
            "request": request,
            "error_message": "Could not retrieve user profile after login.",
        }
        return render_template("partials/_login_form.html", context)

    user_data = me_response.json()

    # Finalize the session with all required user data
    request.session.update({"user_token": token, "user_role": user_data.get("role")})

    response = Response()
    response.headers["HX-Redirect"] = "/dashboard"
    return response


@router.post("/register")
async def handle_register_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    _csrf_token: None = Depends(validate_csrf_token),
    unauthenticated_client_manager: httpx.AsyncClient = Depends(
        get_unauthenticated_bff_api_client
    ),
) -> Response:
    user_data = {"name": name, "email": email, "password": password}
    async with unauthenticated_client_manager as client:
        api_response = await client.post("/auth/register", json=user_data)

    if api_response.status_code == status.HTTP_201_CREATED:
        request.session["toast_message"] = "Registration successful! Please log in."
        request.session["toast_category"] = "success"
        return Response(
            status_code=status.HTTP_200_OK, headers={"HX-Redirect": "/auth/login"}
        )

    else:
        error_message = api_response.json().get(
            "detail", "An unknown registration error occurred."
        )
        context = {
            "request": request,
            "error_message": error_message,
            # Preserve user input on failure
            "submitted_name": name,
            "submitted_email": email,
        }

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

    context = {
        "request": request,
        "title": "Reset Your Password",
        "support_email": settings.SUPPORT_EMAIL,
    }
    response: Response = render_template("forgot-password.html", context)

    return response
