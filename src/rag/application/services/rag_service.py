import logging

from langchain_chroma import Chroma
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langsmith import traceable

from src.assistant.application.protocols import AssistantRepositoryProtocol
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
        assistant_repo: AssistantRepositoryProtocol,
    ):
        self.llm = llm
        self.vector_store = vector_store
        self.prompt = prompt
        self.assistant_repo = assistant_repo

    @traceable(name="Answer Pipeline")
    def answer_query(self, query: str, assistant_id: int) -> str:
        valid_chunk_hashes = self.assistant_repo.get_chunk_hashes_for_assistant(
            assistant_id
        )
        if not valid_chunk_hashes:
            return "No documents have been added to this assistant yet."

        retriever = self.vector_store.as_retriever(
            search_kwargs={
                "k": 4,
                "filter": {"content_hash": {"$in": valid_chunk_hashes}},
            }
        )

        rag_chain = self._build_rag_chain(retriever)
        answer: str = rag_chain.invoke(query)

        return answer

    def _build_rag_chain(self, retriever: VectorStoreRetriever) -> Runnable[str, str]:
        """Builds the RAG chain. Extracted for testability."""

        header = RunnableParallel(
            context=retriever | _format_docs,
            query=RunnablePassthrough(),
        )

        chain: Runnable[str, str] = header | self.prompt | self.llm | StrOutputParser()
        return chain
