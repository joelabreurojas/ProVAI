import datetime
from typing import Any

from jose import jwt

from src.auth.application.protocols import TokenServiceProtocol
from src.core.infrastructure.settings import settings


class TokenService(TokenServiceProtocol):
    """Concrete implementation for JWT handling using python-jose."""

    def create_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()

        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        to_encode.update({"exp": expire})

        token: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return token

    def decode_access_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload: dict[str, Any] = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload

        except jwt.JWTError:
            return None
