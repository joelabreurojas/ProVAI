from fastapi import Depends
from sqlalchemy.orm import Session

from src.auth.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.auth.application.services.auth_service import AuthService
from src.auth.infrastructure.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.security.password_service import PasswordService
from src.auth.infrastructure.security.token_service import TokenService
from src.core.infrastructure.database import get_db

# --- Builder Functions (No FastAPI) ---


def build_password_service() -> PasswordServiceProtocol:
    """Builds a PasswordService."""
    return PasswordService()


def build_token_service() -> TokenServiceProtocol:
    """Builds a TokenService."""
    return TokenService()


def build_user_repository(db: Session) -> UserRepositoryProtocol:
    """Builds a user repository, requiring a database session."""
    return SQLAlchemyUserRepository(db)


# --- Service Builders ---


def build_auth_service(db: Session) -> AuthServiceProtocol:
    """Constructs the AuthService with all its real dependencies."""
    user_repo = build_user_repository(db)
    password_svc = build_password_service()
    token_svc = build_token_service()
    return AuthService(
        user_repo=user_repo, password_svc=password_svc, token_svc=token_svc
    )


# --- FastAPI Dependency Providers ---


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryProtocol:
    """FastAPI dependency provider for the UserRepository."""
    return SQLAlchemyUserRepository(db)


def get_password_service() -> PasswordServiceProtocol:
    """FastAPI dependency provider for the PasswordService."""
    return PasswordService()


def get_token_service() -> TokenServiceProtocol:
    """FastAPI dependency provider for the TokenService."""
    return TokenService()


# --- Service Assembler for FastAPI ---


def get_auth_service(
    user_repo: UserRepositoryProtocol = Depends(get_user_repository),
    password_svc: PasswordServiceProtocol = Depends(get_password_service),
    token_svc: TokenServiceProtocol = Depends(get_token_service),
) -> AuthServiceProtocol:
    """FastAPI dependency provider that assembles the AuthService."""
    return AuthService(
        user_repo=user_repo, password_svc=password_svc, token_svc=token_svc
    )
