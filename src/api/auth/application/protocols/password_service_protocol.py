from typing import Protocol, runtime_checkable


@runtime_checkable
class PasswordServiceProtocol(Protocol):
    """Defines the contract for password hashing and verification."""

    def get_password_hash(self, password: str) -> str: ...
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...
