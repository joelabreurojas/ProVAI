from fastapi import APIRouter, Depends

from src.api.auth.infrastructure.dependencies import get_current_user
from src.core.domain.models import User
from src.core.domain.schemas import UserResponse

TAG = {"name": "Users", "description": "Operations related to users."}

router = APIRouter(prefix="/users", tags=[TAG["name"]])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the profile for the currently authenticated user.
    """
    return current_user
