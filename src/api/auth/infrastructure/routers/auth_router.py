from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.exceptions import HTTPException

from src.api.auth.infrastructure.dependencies import get_auth_service
from src.core.application.exceptions import (
    InvalidPasswordError,
    UserAlreadyExistsError,
)
from src.core.application.protocols import AuthServiceProtocol
from src.core.domain.schemas import Token, UserCreate, UserResponse
from src.core.infrastructure.limiter import limiter

TAG = {"name": "Auth", "description": "User authentication and registration"}

router = APIRouter(prefix="/auth", tags=[TAG["name"]])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Register a new user",
)
@limiter.limit("10/minute")
async def register_user(
    request: Request,
    user_data: UserCreate,
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
) -> UserResponse:
    """
    Handles new user registration.

    - Creates a new user record in the database.
    - Passwords are automatically hashed before storage.
    """

    try:
        new_user = auth_service.register_user(
            name=user_data.name, email=user_data.email, password=user_data.password
        )
        return UserResponse.model_validate(new_user)
    except (UserAlreadyExistsError, InvalidPasswordError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e


@router.post(
    "/token",
    response_model=Token,
    summary="User login to get an access token",
)
@limiter.limit("10/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
) -> Token:
    """
    Handles user login using the OAuth2 password flow.

    - Authenticates the user with their email and password.
    - Returns a JWT access token upon successful authentication.
    """

    _, access_token = auth_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )
    return Token(access_token=access_token, token_type="bearer")
