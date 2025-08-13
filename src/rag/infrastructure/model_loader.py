import logging
from functools import lru_cache

from fastembed import TextEmbedding
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.embeddings import Embeddings

from src.core.constants import PROJECT_ROOT
from src.core.dependencies import get_asset_manager_service
from src.rag.application.exceptions import (
    ModelConfigurationError,
    ModelLoadError,
    ModelNotFoundError,
)

logger = logging.getLogger(__name__)


class FastEmbedLangChain(Embeddings):
    def __init__(self, model: TextEmbedding):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # fastembed returns numpy arrays, so convert them to lists
        return [e.tolist() for e in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.model.embed(text)[0].tolist()


@lru_cache(maxsize=1)
def get_llm() -> LlamaCpp:
    asset_manager = get_asset_manager_service()
    llm_config = asset_manager.get_llm_config()
    if not llm_config.filename:
        raise ModelConfigurationError(asset_type="LLM", field="filename")
    model_file_path = PROJECT_ROOT / "models" / llm_config.filename
    if not model_file_path.exists():
        raise ModelNotFoundError(model_path=model_file_path)
    try:
        llm = LlamaCpp(
            model_path=str(model_file_path),
            n_ctx=2048,  # Context size
            n_gpu_layers=0,  # Explicitly run on CPU
            verbose=False,
            max_tokens=512,  # Maximum tokens to generate
            temperature=0.7,
        )
    except Exception as e:
        raise ModelLoadError() from e
    return llm
