import datetime
from datetime import timedelta
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from src.core.application.exceptions import (
    TokenExpiredError,
    TokenValidationError,
)
from src.core.application.protocols import TokenServiceProtocol
from src.core.infrastructure.settings import settings


class TokenService(TokenServiceProtocol):
    """Concrete implementation for JWT handling using python-jose."""

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(datetime.UTC) + expires_delta
        else:
            expire = datetime.datetime.now(datetime.UTC) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})

        token: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return token

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """
        Decodes a JWT. Raises specific exceptions for different failure modes.
        """
        try:
            payload: dict[str, Any] = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload

        except ExpiredSignatureError as e:
            raise TokenExpiredError() from e

        except JWTError as e:
            raise TokenValidationError() from e
