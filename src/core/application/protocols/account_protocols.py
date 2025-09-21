from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.core.domain.models import User
    from src.core.domain.schemas import UserUpdate


@runtime_checkable
class AccountServiceProtocol(Protocol):
    """
    Defines the contract for the service responsible for managing user
    account settings.
    """

    def update_profile(self, user: "User", user_update: "UserUpdate") -> "User": ...

    def update_password(
        self, user: "User", current_password: str, new_password: str
    ) -> None: ...

    def delete_account(self, user: "User") -> None: ...
