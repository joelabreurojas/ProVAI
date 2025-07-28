from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.auth.domain.models import User
    from src.auth.domain.schemas import UserCreate


@runtime_checkable
class UserRepositoryProtocol(Protocol):
    """Defines the contract for the user data repository."""

    def get_by_email(self, email: str) -> "User" | None: ...
    def add(self, user_create: "UserCreate", hashed_password: str) -> "User": ...
