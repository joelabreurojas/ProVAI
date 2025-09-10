from fastapi import Depends, HTTPException, Request, status

from src.api.auth.application.exceptions import TokenValidationError, UserNotFoundError
from src.api.auth.application.protocols import AuthServiceProtocol
from src.api.auth.dependencies import get_auth_service
from src.api.auth.domain.models import User


def get_current_user_from_cookie(
    request: Request,
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
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
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
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
        # If the token is invalid for any reason, treat them as logged out.
        return None
