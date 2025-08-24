from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as SQLAlchemySession

from src.auth.application.exceptions import TokenValidationError
from src.auth.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.auth.application.services import AuthService
from src.auth.domain.models import User
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.auth.infrastructure.security import PasswordService, TokenService
from src.core.infrastructure.database import get_db

# --- Authentication Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# --- Protocol Implementations ---
def get_user_repository(
    db: SQLAlchemySession = Depends(get_db),
) -> UserRepositoryProtocol:
    return SQLAlchemyUserRepository(db)


def get_password_service() -> PasswordServiceProtocol:
    return PasswordService()


def get_token_service() -> TokenServiceProtocol:
    return TokenService()


# --- Service Assembler ---
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
    authenticated user or raises a 401 HTTPException if authentication fails.
    """
    try:
        return auth_service.get_user_from_token(token)
    except TokenValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
