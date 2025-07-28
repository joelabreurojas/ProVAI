from src.auth.application.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from src.auth.application.protocols import (
    AuthServiceProtocol,
    PasswordServiceProtocol,
    TokenServiceProtocol,
    UserRepositoryProtocol,
)
from src.auth.domain.models import User
from src.auth.domain.schemas import UserCreate


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

    def register_user(self, user_create: UserCreate) -> User:
        db_user = self.user_repo.get_by_email(user_create.email)

        if db_user:
            raise UserAlreadyExistsError()

        hashed_password = self.password_svc.get_password_hash(user_create.password)
        return self.user_repo.add(user_create, hashed_password)

    def authenticate_user(self, email: str, password: str) -> tuple[User, str]:
        user = self.user_repo.get_by_email(email)

        if not user or not self.password_svc.verify_password(
            password, user.hashed_password
        ):
            raise InvalidCredentialsError()

        token_data = {"sub": user.email, "role": user.role}
        access_token = self.token_svc.create_access_token(data=token_data)

        return user, access_token
