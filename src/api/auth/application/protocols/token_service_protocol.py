from datetime import timedelta
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TokenServiceProtocol(Protocol):
    """Defines the contract for JWT creation and decoding."""

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str: ...
    def decode_access_token(self, token: str) -> dict[str, Any] | None: ...
