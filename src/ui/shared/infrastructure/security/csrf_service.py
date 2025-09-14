import time

from itsdangerous import BadTimeSignature, SignatureExpired, URLSafeTimedSerializer
from starlette import status
from starlette.exceptions import HTTPException

from src.core.infrastructure.settings import settings


class CSRFService:
    """
    A service for generating and validating CSRF tokens using itsdangerous.
    """

    def __init__(self, secret_key: str):
        self.serializer = URLSafeTimedSerializer(secret_key, salt="csrf-token")

    def generate_token(self) -> str:
        """Generates a new CSRF token."""
        return self.serializer.dumps(time.time())

    def validate_token(self, token: str, max_age_seconds: int = 3600) -> bool:
        """
        Validates a CSRF token. Returns True if valid, otherwise raises an exception.
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token is missing."
            )
        try:
            self.serializer.loads(token, max_age=max_age_seconds)
            return True
        except SignatureExpired as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token has expired."
            ) from e
        except BadTimeSignature as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token is invalid."
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token is invalid."
            ) from e


# Singleton instance to be used by dependencies
csrf_service = CSRFService(secret_key=settings.SECRET_KEY)
