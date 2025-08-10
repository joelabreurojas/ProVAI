import logging

from langchain_chroma import Chroma
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langsmith import traceable

from src.rag.application.protocols import RAGServiceProtocol

logger = logging.getLogger(__name__)


def _format_docs(docs: list[Document]) -> str:
    """Combines the page_content of retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


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

    @traceable(name="Answer Pipeline")
    def answer_query(self, query: str, chat_id: int) -> str:
        """
        Takes a user query and chat_id, runs the full RAG pipeline with
        filtering, and returns the answer.
        """
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 4, "filter": {"chat_id": chat_id}}
        )
        rag_chain = self._build_rag_chain(retriever)
        answer: str = rag_chain.invoke(query)
        return answer

    def _build_rag_chain(self, retriever) -> Runnable:
        """Builds the RAG chain. Extracted for testability."""
        return (
            {"context": retriever | _format_docs, "query": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
