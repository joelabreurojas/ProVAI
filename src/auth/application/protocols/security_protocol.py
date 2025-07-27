from typing import Any, Protocol, runtime_checkable


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
