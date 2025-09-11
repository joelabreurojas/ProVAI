import logging

from langsmith import traceable
from pydantic import ValidationError

from src.api.auth.application.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
    TokenMissingDataError,
    TokenValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.api.auth.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.api.auth.domain.models import User
from src.api.auth.domain.schemas import UserCreate

logger = logging.getLogger(__name__)


class AuthService(AuthServiceProtocol):
    """
    The main application service for handling all authentication-related
    business logic. It acts as a pure orchestrator.
    """

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        password_svc: PasswordServiceProtocol,
        token_svc: TokenServiceProtocol,
    ):
        self.user_repo = user_repo
        self.password_svc = password_svc
        self.token_svc = token_svc

    @traceable(name="Register User")
    def register_user(self, name: str, email: str, password: str) -> User:
        try:
            user_data = UserCreate(name=name, email=email, password=password)
        except ValidationError as e:
            raise InvalidPasswordError() from e

        db_user = self.user_repo.get_by_email(user_data.email)
        if db_user:
            raise UserAlreadyExistsError()

        hashed_password = self.password_svc.get_password_hash(user_data.password)
        return self.user_repo.add(user_data, hashed_password)

    @traceable(name="Authenticate User")
    def authenticate_user(self, email: str, password: str) -> tuple[User, str]:
        user = self.user_repo.get_by_email(email)

        if not user or not self.password_svc.verify_password(
            password, user.hashed_password
        ):
            raise InvalidCredentialsError()

        token_data = {"sub": user.email, "role": user.role}
        access_token = self.token_svc.create_access_token(data=token_data)

        return user, access_token

    def get_user_from_token(self, token: str) -> User:
        """
        Validates a JWT, decodes it, and retrieves the user.
        """
        try:
            payload = self.token_svc.decode_access_token(token)

            if payload is None:
                raise TokenValidationError()

            email: str | None = payload.get("sub")
            if not email:
                raise TokenMissingDataError(missing_claim="sub")

            user = self.user_repo.get_by_email(email)
            if not user:
                raise UserNotFoundError()

            return user

        except (UserNotFoundError, TokenValidationError) as e:
            raise e

        except Exception as e:
            logger.error(
                "An unexpected error occurred during token validation.", exc_info=e
            )
            raise e

    def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email address."""
        return self.user_repo.get_by_email(email)
