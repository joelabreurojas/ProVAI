from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.auth.domain.schemas import UserCreate


@runtime_checkable
class AuthServiceProtocol(Protocol):
    """Defines the contract for the main authentication service."""

    def register_user(self, user_create: "UserCreate") -> "User": ...
    def authenticate_user(self, email: str, password: str) -> tuple["User", str]: ...
