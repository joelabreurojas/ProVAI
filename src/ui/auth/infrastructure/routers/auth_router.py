import httpx
from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse

from src.core.domain.models import User
from src.core.infrastructure.settings import settings
from src.ui.shared.infrastructure.dependencies import (
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
) -> Response:
    async with unauthenticated_client_manager as client:
        client_response = await client.post(
            "/auth/token", data={"email": email, "password": password}
        )

    if client_response.status_code != status.HTTP_200_OK:
        error_message = client_response.json().get("message", "Login failed.")
        context = {"request": request, "error_message": error_message}
        return render_template("partials/_login_form.html", context)

    token_data = client_response.json()
    token = token_data.get("access_token")

    # Temporary client to fetch the user's profile.
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(
        base_url=f"{settings.INTERNAL_API_URL}{settings.API_ROOT_PATH}",
        headers=headers,
    ) as authenticated_client:
        me_response = await authenticated_client.get("/users/me")

    if me_response.status_code != status.HTTP_200_OK:
        context = {
            "request": request,
            "error_message": "Could not retrieve user profile after login.",
        }
        response: Response = render_template("partials/_login_form.html", context)

        return response

    user_data = me_response.json()

    # Populate the session with data from the /users/me endpoint.
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
        client_response = await client.post("/auth/register", json=user_data)

    if client_response.status_code == status.HTTP_201_CREATED:
        request.session["toast_message"] = "Registration successful! Please log in."
        request.session["toast_category"] = "success"
        return Response(
            status_code=status.HTTP_200_OK, headers={"HX-Redirect": "/auth/login"}
        )
    else:
        error_message = "An unknown registration error occurred."
        try:
            error_json = client_response.json()
            # Handle Pydantic's detailed validation errors (422)
            if "detail" in error_json and isinstance(error_json["detail"], list):
                # Get the message from the first error object
                raw_msg = error_json["detail"][0].get("msg", "Invalid input.")
                # Clean up the "Value error, " prefix if Pydantic adds it
                if raw_msg.startswith("Value error, "):
                    error_message = raw_msg.split(", ", 1)[1]
                else:
                    error_message = raw_msg
            # Handle our custom application exceptions (e.g., 409 Conflict)
            elif "message" in error_json:
                error_message = error_json["message"]
            # Fallback for other FastAPI errors
            elif "detail" in error_json:
                error_message = error_json["detail"]

        except (KeyError, IndexError, AttributeError, TypeError):
            # If the JSON structure is unexpected, use a generic message
            error_message = "An unexpected error occurred during registration."

        context = {"request": request, "error_message": error_message}
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
