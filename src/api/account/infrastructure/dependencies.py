from fastapi import Depends

from src.api.account.application.services.account_service import AccountService
from src.api.auth.infrastructure.dependencies import (
    get_password_service,
    get_user_repository,
)
from src.core.application.protocols import (
    AccountServiceProtocol,
    PasswordServiceProtocol,
    UserRepositoryProtocol,
)
from src.core.infrastructure.utils import provides


@provides(AccountServiceProtocol)
def get_account_service(
    user_repo: UserRepositoryProtocol = Depends(get_user_repository),
    password_svc: PasswordServiceProtocol = Depends(get_password_service),
) -> AccountServiceProtocol:
    return AccountService(user_repo=user_repo, password_svc=password_svc)
