from src.core.application.exceptions import InvalidCredentialsError
from src.core.application.protocols import (
    PasswordServiceProtocol,
    UserRepositoryProtocol,
)
from src.core.domain.models import User
from src.core.domain.schemas import UserUpdate


class AccountService:
    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        password_svc: PasswordServiceProtocol,
    ):
        self.user_repo = user_repo
        self.password_svc = password_svc

    def update_profile(self, user: User, user_update: UserUpdate) -> User:
        return self.user_repo.update(user, user_update)

    def update_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        if not self.password_svc.verify_password(
            current_password, user.hashed_password
        ):
            raise InvalidCredentialsError(
                "The current password you entered is incorrect."
            )

        new_hashed_password = self.password_svc.get_password_hash(new_password)
        self.user_repo.update_password(user, new_hashed_password)

    def delete_account(self, user: User) -> None:
        self.user_repo.delete(user)
