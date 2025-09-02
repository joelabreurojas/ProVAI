from fastapi import APIRouter

from src.api.core.infrastructure.settings import settings

TAG = {"name": "API Root", "description": "The root of the API."}

router = APIRouter(tags=[TAG["name"]])


@router.get("/", summary="Welcome message")
async def read_api_root() -> dict[str, str]:
    """A welcome message to confirm that the API is running."""
    return {"message": f"Welcome to the {settings.TITLE} API"}
