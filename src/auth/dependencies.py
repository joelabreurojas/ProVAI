from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from src.auth.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.auth.application.services import AuthService
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.auth.infrastructure.security import PasswordService, TokenService
from src.core.infrastructure.database import get_db


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
