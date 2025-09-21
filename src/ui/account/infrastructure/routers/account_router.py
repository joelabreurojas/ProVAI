import httpx
from fastapi import APIRouter, Depends, Form, Request, Response, status

from src.ui.shared.infrastructure.dependencies import (
    get_authenticated_bff_api_client,
    get_sidebar_context,
    validate_csrf_token,
)
from src.ui.shared.infrastructure.utils import htmx_refresh_csrf, render_template

router = APIRouter(prefix="/account", tags=["UI - Account"], include_in_schema=False)


@router.get("")
async def serve_account_page(
    request: Request,
    sidebar_context: dict = Depends(get_sidebar_context),
) -> Response:
    """
    Serves the main account management page, inheriting the shared app layout.
    """
    context = {
        "request": request,
        "title": "Your Account",
        "navbar_type": "app",
        **sidebar_context,  # Provides 'user' and 'tutors' for the layout
    }
    response: Response = render_template("account.html", context)

    return response


@router.post("/profile")
async def handle_update_profile(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    _csrf: None = Depends(validate_csrf_token),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
) -> Response:
    """BFF endpoint to handle profile update form submission."""
    async with authenticated_client_manager as client:
        client_response = await client.patch(
            "/account/profile", json={"name": name, "email": email}
        )

    if client_response.status_code == status.HTTP_200_OK:
        context = {
            "request": request,
            "toast_category": "success",
            "toast_message": "Profile updated successfully!",
        }
        response: Response = htmx_refresh_csrf(
            render_template("partials/_toast.html", context), request
        )

        return response

    else:
        error_message = client_response.json().get(
            "detail", "Failed to update profile."
        )
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": error_message,
        }
        response: Response = render_template("partials/_toast.html", context)

        return response


@router.post("/password")
async def handle_update_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    _csrf: None = Depends(validate_csrf_token),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
) -> Response:
    """BFF endpoint to handle password update form submission."""
    payload = {
        "current_password": current_password,
        "new_password": new_password,
        "confirm_password": confirm_password,
    }
    async with authenticated_client_manager as client:
        client_response = await client.patch("/account/password", json=payload)

    if client_response.status_code == status.HTTP_204_NO_CONTENT:
        context = {
            "request": request,
            "toast_category": "success",
            "toast_message": "Password updated successfully!",
        }
        response: Response = htmx_refresh_csrf(
            render_template("partials/_toast.html", context), request
        )

        return response

    else:
        error_message = client_response.json().get(
            "detail", "Failed to update password."
        )
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": error_message,
        }
        response: Response = render_template("partials/_toast.html", context)

        return response


@router.post("/delete")
async def handle_delete_account(
    request: Request,
    _csrf: None = Depends(validate_csrf_token),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
) -> Response:
    """BFF endpoint to handle the account deletion confirmation."""
    async with authenticated_client_manager as client:
        client_response = await client.delete("/account")

    if client_response.status_code == status.HTTP_204_NO_CONTENT:
        request.session.clear()
        response = Response()
        response.headers["HX-Redirect"] = "/"

        return response
    else:
        error_message = client_response.json().get(
            "detail", "Failed to delete account."
        )
        context = {
            "request": request,
            "toast_category": "error",
            "toast_message": error_message,
        }
        response: Response = render_template("partials/_toast.html", context)

        return response
