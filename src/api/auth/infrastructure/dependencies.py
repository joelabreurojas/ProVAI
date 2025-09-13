from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.auth.application.services import AuthService
from src.api.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.api.auth.infrastructure.security import PasswordService, TokenService
from src.core.application.exceptions import (
    TokenValidationError,
    UserNotFoundError,
)
from src.core.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.core.domain.models import User
from src.core.infrastructure.database import get_db
from src.core.infrastructure.utils import provides

# --- Authentication Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# --- Protocol Implementations ---


@provides(UserRepositoryProtocol)
def get_user_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> UserRepositoryProtocol:
    return SQLAlchemyUserRepository(db)


@provides(PasswordServiceProtocol)
def get_password_service() -> PasswordServiceProtocol:
    return PasswordService()


@provides(TokenServiceProtocol)
def get_token_service() -> TokenServiceProtocol:
    return TokenService()


# --- Service Assembler ---
@provides(AuthServiceProtocol)
def get_auth_service(
    user_repo: UserRepositoryProtocol = Depends(get_user_repository),
    password_svc: PasswordServiceProtocol = Depends(get_password_service),
    token_svc: TokenServiceProtocol = Depends(get_token_service),
) -> AuthServiceProtocol:
    return AuthService(
        user_repo=user_repo, password_svc=password_svc, token_svc=token_svc
    )


# --- Endpoint Dependency ---
def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthServiceProtocol = Depends(get_auth_service),
) -> User:
    """
    The primary dependency for protected endpoints. It provides the currently
    authenticated user or raises a HTTPException if auth fails.
    """
    try:
        return auth_service.get_user_from_token(token)
    except (TokenValidationError, UserNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during authentication.",
        ) from e
