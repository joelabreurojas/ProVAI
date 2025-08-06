import logging
from operator import itemgetter
from typing import Any

from langchain_community.llms.llamacpp import LlamaCpp
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel

from src.rag.application.protocols import RAGServiceProtocol

logger = logging.getLogger(__name__)


def _format_docs(docs: list[Document]) -> str:
    """Combines the page_content of retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


def _parse_llm_output(response: dict[str, str]) -> str:
    """
    Safely parses the output from the Llama LLM.
    Checks for the presence of 'choices' and that it's a non-empty list.
    """
    if (
        "choices" in response
        and isinstance(response["choices"], list)
        and len(response["choices"]) > 0
    ):
        if "text" in response["choices"][0]:
            return response["choices"][0]["text"].strip()

    logger.warning("LLM output was not in the expected format. Response: %s", response)
    return "I'm sorry, I was unable to generate a response."


class RAGService(RAGServiceProtocol):
    """
    The main service for handling the RAG pipeline using LCEL.
    """

    def __init__(
        self,
        llm: LlamaCpp,
        vector_store: Chroma,
        prompt: ChatPromptTemplate,
    ):
        self.llm = llm
        self.vector_store = vector_store
        self.prompt = prompt

        def create_filtered_retriever(
            input_dict: dict[str, Any],
        ) -> Runnable[str, list[Document]]:
            """Creates a retriever filtered by the chat_id from the input."""
            chat_id = input_dict.get("chat_id")

            return self.vector_store.as_retriever(
                search_kwargs={"k": 4, "filter": {"chat_id": chat_id}}
            )

        self.rag_chain: Runnable[dict[str, Any], str] = (
            RunnableParallel(
                question=itemgetter("query"),
                chat_id=itemgetter("chat_id"),
            )
            | {
                "context": lambda x: create_filtered_retriever(x).invoke(x["question"]),
                "question": itemgetter("question"),
            }
            | RunnableParallel(
                context=(lambda x: _format_docs(x["context"])),
                question=itemgetter("question"),
            )
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def answer_query(self, query: str, chat_id: int) -> str:
        """
        Takes a user query and chat_id, runs the full RAG pipeline with
        filtering, and returns the answer.
        """
        answer: str = self.rag_chain.invoke({"query": query, "chat_id": chat_id})

        return answer
