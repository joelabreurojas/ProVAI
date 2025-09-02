from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.api.auth.domain.models import User
    from src.api.auth.domain.schemas import UserCreate


@runtime_checkable
class AuthServiceProtocol(Protocol):
    """Defines the contract for the main authentication service."""

    def register_user(self, user_create: "UserCreate") -> "User": ...

    def authenticate_user(self, email: str, password: str) -> tuple["User", str]: ...

    def get_user_from_token(self, token: str) -> "User": ...

    def get_user_by_email(self, email: str) -> Optional["User"]: ...
