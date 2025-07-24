from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.auth.domain.schemas import UserCreate


@runtime_checkable
class PasswordServiceProtocol(Protocol):
    """Defines the contract for password hashing and verification."""

    def get_password_hash(self, password: str) -> str: ...
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...


@runtime_checkable
class TokenServiceProtocol(Protocol):
    """Defines the contract for JWT creation and decoding."""

    def create_access_token(self, data: dict[str, Any]) -> str: ...
    def decode_access_token(self, token: str) -> dict[str, Any] | None: ...


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    """Defines the contract for the user data repository."""

    def get_by_email(self, email: str) -> "User" | None: ...
    def add(self, user_create: "UserCreate", hashed_password: str) -> "User": ...


@runtime_checkable
class AuthServiceProtocol(Protocol):
    """Defines the contract for the main authentication service."""

    def register_user(self, user_create: "UserCreate") -> "User": ...
    def authenticate_user(self, email: str, password: str) -> tuple["User", str]: ...
