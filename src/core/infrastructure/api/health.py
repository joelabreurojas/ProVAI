from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.infrastructure.database import get_db

router = APIRouter()


@router.get("/health", tags=["Status"])
async def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Checks if the API is running and can connect to the database."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return {"api_status": "ok", "db_status": db_status}
