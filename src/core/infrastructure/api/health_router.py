from fastapi import APIRouter, Depends
import chromadb
from sqlalchemy import text
from sqlalchemy.orm import Session as SQLAlchemySession

from src.ai.dependencies import get_embedding_service, get_llm_service
from src.ai.application.protocols import (
    EmbeddingServiceProtocol,
    LLMServiceProtocol,
)
from src.core.constants import PROJECT_ROOT
from src.core.infrastructure.database import get_db

TAG: dict[str, str] = {"name": "Status", "description": "API health and monitoring"}

router = APIRouter(tags=[TAG["name"]])


def get_health_check_vector_store_client() -> chromadb.PersistentClient:
    """Provides a lightweight ChromaDB client specifically for fast health checks."""
    persist_dir_path = str(PROJECT_ROOT / "vector_store")
    return chromadb.PersistentClient(path=persist_dir_path)


@router.get("/health", summary="Perform a lightweight health check")
async def health_check(
    db: SQLAlchemySession = Depends(get_db),
    vector_store_client: chromadb.PersistentClient = Depends(
        get_health_check_vector_store_client
    ),
) -> dict[str, str]:
    """
    Checks the status of basic external services (database, vector store)
    without loading the heavy AI models. This endpoint is designed for fast,
    high-frequency checks by load balancers or uptime monitors.
    """
    db_status = "ok"
    vector_store_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"

    try:
        vector_store_client.heartbeat()
    except Exception as e:
        vector_store_status = f"error: {e}"

    return {
        "api_status": "ok",
        "db_status": db_status,
        "vector_store_status": vector_store_status,
    }


@router.get("/status", summary="Perform a comprehensive status check")
async def comprehensive_status_check(
    health_status: dict[str, str] = Depends(health_check),
    llm_service: LLMServiceProtocol = Depends(get_llm_service),
    embedding_service: EmbeddingServiceProtocol = Depends(get_embedding_service),
) -> dict[str, str]:
    """
    Performs a full diagnostic check of all application components, including
    the AI models. This can be slow and should be used for diagnostics, not
    high-frequency health probes.
    """
    llm_status = "ok"
    embedding_model_status = "ok"

    try:
        llm_service.get_llm()
    except Exception as e:
        llm_status = f"error: {e}"

    try:
        embedding_service.get_embedding_model()
    except Exception as e:
        embedding_model_status = f"error: {e}"

    return {
        **health_status,
        "llm_status": llm_status,
        "embedding_model_status": embedding_model_status,
    }
