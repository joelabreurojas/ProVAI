"""
This module serves as the Composition Root for the application.

It is the single place where all abstract protocols are wired to their
concrete implementations from the infrastructure layer. FastAPI's `Depends`
will use the provider functions defined here to inject dependencies into
the API endpoints and other services.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

# --- Auth Protocols ---
from src.auth.application.protocols import (
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)

# --- Auth Concrete Implementations ---
from src.auth.infrastructure.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.security.password_service import PasswordService
from src.auth.infrastructure.security.token_service import TokenService

# --- Core Dependencies ---
from src.core.infrastructure.database import get_db

# --- Protocol Implementations (The "Wiring") ---


def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryProtocol:
    """Provides a concrete SQLAlchemy implementation of the UserRepositoryProtocol."""
    return SQLAlchemyUserRepository(db)


def get_password_service() -> PasswordServiceProtocol:
    """Provides a concrete implementation of the PasswordServiceProtocol."""
    return PasswordService()


def get_token_service() -> TokenServiceProtocol:
    """Provides a concrete implementation of the TokenServiceProtocol."""
    return TokenService()
