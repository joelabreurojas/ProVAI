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

from src.rag.dependencies import get_rag_embedding_model, get_rag_llm


def main() -> None:
    """Verifies model loading and basic functionality."""
    load_dotenv()

    print("--- Verifying LLM ---")
    llm = get_rag_llm()
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
    embedding_model = get_rag_embedding_model()
    text = "This is a test sentence."
    embedding = embedding_model.embed_query(text)

    print(f"Text: {text}")
    print(f"Embedding vector (first 5 dimensions): {embedding[:5]}")
    print(f"Total embedding dimensions: {len(embedding)}")
    print("-" * 20)


if __name__ == "__main__":
    main()
