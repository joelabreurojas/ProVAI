import logging
from functools import lru_cache

import psutil
from langchain_huggingface import HuggingFaceEmbeddings
from llama_cpp import Llama

from src.core.constants import PROJECT_ROOT

logger = logging.getLogger(__name__)


def _log_memory_usage() -> None:
    """Logs the current memory usage of the process."""
    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"Current memory usage: {memory_info.rss / 1024**2:.2f} MB")


@lru_cache(maxsize=1)
def get_llm() -> Llama:
    """
    Loads and returns the Llama C++ model.
    Uses lru_cache to ensure the model is loaded only once (singleton).
    """
    logger.info("Starting to load the LLM...")
    _log_memory_usage()

    model_file_path = PROJECT_ROOT / "models" / "phi-2.Q4_K_M.gguf"

    llm = Llama(
        model_path=str(model_file_path),
        n_ctx=2048,  # The maximum context size
        n_gpu_layers=0,  # Explicitly run on CPU
        verbose=False,
    )

    logger.info("LLM loaded successfully.")
    _log_memory_usage()
    return llm


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Loads and returns the sentence-transformer embedding model.
    Uses lru_cache to ensure the model is loaded only once (singleton).
    """
    logger.info("Starting to load the embedding model...")
    _log_memory_usage()

    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}

    embedding_model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )

    logger.info("Embedding model loaded successfully.")
    _log_memory_usage()
    return embedding_model
