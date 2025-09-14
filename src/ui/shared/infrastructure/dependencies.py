from fastapi import Depends, Form, HTTPException, Request, status

from src.core.application.exceptions import TokenValidationError, UserNotFoundError
from src.core.application.protocols import AuthServiceProtocol, TutorServiceProtocol
from src.core.domain.models import User
from src.ui.shared.infrastructure.security import csrf_service


def get_csrf_token(request: Request) -> str:
    """
    Generates a CSRF token and stores it in the session if it doesn't exist.
    Returns the token. This should be used when rendering forms.
    """
    if "csrf_token" not in request.session:
        token = csrf_service.generate_token()
        request.session["csrf_token"] = token
    else:
        token = request.session["csrf_token"]
    return token


async def validate_csrf_token(
    request: Request,
    csrf_token: str = Form(..., alias="csrf_token"),
) -> None:
    """
    A dependency that validates the CSRF token from a form submission against
    the one stored in the session.
    """
    stored_token = request.session.get("csrf_token")
    if (
        not stored_token
        or not csrf_service.validate_token(csrf_token)
        or csrf_token != stored_token
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing CSRF token.",
        )


def get_current_user_from_cookie(
    request: Request,
    auth_service: AuthServiceProtocol = Depends(),
) -> User:
    """
    The single dependency for protecting UI routes.
    It reads the JWT from the session cookie, validates it, and returns the User.
    If the token is missing or invalid, it raises a 401 HTTPException.
    """
    token = request.session.get("user_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        user = auth_service.get_user_from_token(token)
        return user
    except (UserNotFoundError, TokenValidationError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from e


def get_optional_current_user_from_cookie(
    request: Request,
    auth_service: AuthServiceProtocol = Depends(),
) -> User | None:
    """
    A dependency that returns the current user if they are authenticated via
    a session cookie, but returns None if they are not. It never raises an error.
    """
    token = request.session.get("user_token")
    if not token:
        return None

    try:
        user = auth_service.get_user_from_token(token)
        return user
    except (UserNotFoundError, TokenValidationError):
        # If the auth is invalid for any reason, treat them as logged out.
        return None


def get_sidebar_context(
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> dict:
    """
    A dependency that provides all necessary context for rendering the
    shared application layout, including the user and their tutors.
    """
    tutors = tutor_service.get_tutors_for_user(user)
    return {"user": user, "tutors": tutors}
