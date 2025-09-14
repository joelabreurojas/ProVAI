from fastapi import APIRouter, Depends, HTTPException, status

from src.api.account.application.services.account_service import AccountServiceProtocol
from src.api.account.infrastructure.dependencies import get_account_service
from src.api.auth.infrastructure.dependencies import get_current_user
from src.core.application.exceptions import (
    InvalidCredentialsError,
    InvalidPasswordError,
)
from src.core.domain.models import User
from src.core.domain.schemas import PasswordUpdate, UserResponse, UserUpdate

TAG = {"name": "Account", "description": "Manage user account settings."}
router = APIRouter(prefix="/account", tags=[TAG["name"]])


@router.patch("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceProtocol = Depends(get_account_service),
) -> UserResponse:
    updated_user = account_service.update_profile(current_user, user_data)
    return UserResponse.model_validate(updated_user)


@router.patch("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceProtocol = Depends(get_account_service),
):
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password and confirmation do not match.",
        )
    try:
        account_service.update_password(
            current_user, password_data.current_password, password_data.new_password
        )
    except (InvalidCredentialsError, InvalidPasswordError) as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    account_service: AccountServiceProtocol = Depends(get_account_service),
):
    account_service.delete_account(current_user)
