"""
A simple script to verify that the AI models can be loaded
and used via the dependency injection system.

python -m scripts.verify_models

NOTE: This script assumes that the application's logging is configured
elsewhere (e.g., in the main app factory). It is a simple client
of the dependency providers.
"""

from typing import Iterator

from dotenv import load_dotenv

from src.api.ai.infrastructure.dependencies import (
    get_embedding_service,
    get_llm_service,
)


def main() -> None:
    """Verifies model loading and basic functionality."""
    load_dotenv()
    print("--- Verifying LLM ---")

    print("Loading LLM...")
    llm_service = get_llm_service()
    llm = llm_service.get_llm()
    print("LLM loaded successfully.")

    print("\nLoading Embedding Model...")
    embedding_service = get_embedding_service()
    embedding_model = embedding_service.get_embedding_model()
    print("Embedding Model loaded successfully.")

    prompt = "What is the capital of France?"
    print(f"Prompt: {prompt}")

    # LlamaCpp may log directly
    output = llm(prompt, max_tokens=32, stop=["\n"], echo=False)
    answer = "No response generated."

    if isinstance(output, dict):
        answer = output["choices"][0]["text"]
    elif isinstance(output, Iterator):
        answer = "Streamed response (not fully processed in this script)."

    print(f"LLM Answer: {answer}")
    print("-" * 20)

    print("\n--- Verifying Embedding Model ---")
    text = "This is a test sentence."
    embedding = embedding_model.embed_query(text)

    print(f"Text: {text}")
    print(f"Embedding vector (first 5 dimensions): {embedding[:5]}")
    print(f"Total embedding dimensions: {len(embedding)}")
    print("-" * 20)


if __name__ == "__main__":
    main()
