from datetime import timedelta
from typing import TYPE_CHECKING, Any, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.core.domain.models import User
    from src.core.domain.schemas import UserCreate


@runtime_checkable
class AuthServiceProtocol(Protocol):
    """Defines the contract for the main authentication service."""

    def register_user(self, name: str, email: str, password: str) -> "User": ...

    def authenticate_user(self, email: str, password: str) -> tuple["User", str]: ...

    def get_user_from_token(self, token: str) -> "User": ...

    def get_user_by_email(self, email: str) -> Optional["User"]: ...


@runtime_checkable
class PasswordServiceProtocol(Protocol):
    """Defines the contract for password hashing and verification."""

    def get_password_hash(self, password: str) -> str: ...

    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...


@runtime_checkable
class TokenServiceProtocol(Protocol):
    """Defines the contract for JWT creation and decoding."""

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str: ...

    def decode_access_token(self, token: str) -> dict[str, Any] | None: ...


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    """Defines the contract for the user data repository."""

    def get_by_email(self, email: str) -> Optional["User"]: ...

    def get_by_id(self, user_id: int) -> Optional["User"]: ...

    def add(self, user_create: "UserCreate", hashed_password: str) -> "User": ...
