from typing import Protocol, runtime_checkable

from langchain_community.llms.llamacpp import LlamaCpp


@runtime_checkable
class LLMServiceProtocol(Protocol):
    """Defines the contract for the Language Model service."""

    def get_llm(self) -> LlamaCpp: ...
