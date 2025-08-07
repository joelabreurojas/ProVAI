from operator import itemgetter
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel
from llama_cpp import Llama

from src.rag.application.protocols import RAGServiceProtocol


def _format_docs(docs: list[Document]) -> str:
    """Combines the page_content of retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


class RAGService(RAGServiceProtocol):
    """
    The main service for handling the RAG pipeline using LCEL.
    """

    def __init__(
        self,
        llm: Llama,
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
            | (lambda prompt_value: prompt_value.to_string())
            | self.llm
            | itemgetter("choices")
            | (lambda choices: choices[0]["text"])
        )

    def answer_query(self, query: str, chat_id: int) -> str:
        """
        Takes a user query and chat_id, runs the full RAG pipeline with
        filtering, and returns the answer.
        """
        answer: str = self.rag_chain.invoke({"query": query, "chat_id": chat_id})

        return answer
