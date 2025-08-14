import hashlib
import logging
import tempfile

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document as LangChainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.chat.application.protocols import ContentRepositoryProtocol
from src.rag.application.protocols import IngestionServiceProtocol

logger = logging.getLogger(__name__)


class IngestionService(IngestionServiceProtocol):
    def __init__(
        self,
        vector_store: Chroma,
        text_splitter: RecursiveCharacterTextSplitter,
        content_repo: ContentRepositoryProtocol,
    ):
        self.vector_store = vector_store
        self.text_splitter = text_splitter
        self.content_repo = content_repo

    def ingest_document(self, file_bytes: bytes, file_name: str, chat_id: int) -> None:
        """
        Processes a PDF, creating relational records for documents and chunks,
        and storing embeddings in the vector store. This process is idempotent.
        """
        db_document = self.content_repo.create_document(
            file_name=file_name, chat_id=chat_id
        )

        langchain_docs = self._load_pdf_from_bytes(file_bytes)
        chunks = self._split_documents(langchain_docs)

        chunks_to_add_to_vector_store = []
        chunk_ids_for_vector_store = []

        for chunk_doc in chunks:
            chunk_content = chunk_doc.page_content
            content_hash = hashlib.sha256(chunk_content.encode("utf-8")).hexdigest()

            db_chunk = self.content_repo.get_chunk_by_hash(content_hash)

            if not db_chunk:
                db_chunk = self.content_repo.create_chunk(
                    content_hash=content_hash, content=chunk_content
                )
                chunks_to_add_to_vector_store.append(chunk_content)
                chunk_ids_for_vector_store.append(content_hash)

            self.content_repo.link_chunk_to_document(db_document, db_chunk)

        if chunks_to_add_to_vector_store:
            self.vector_store.add_texts(
                texts=chunks_to_add_to_vector_store, ids=chunk_ids_for_vector_store
            )

        logger.info(
            f"Successfully ingested '{file_name}' for chat_id {chat_id}. "
            f"Added {len(chunks_to_add_to_vector_store)} new unique chunks "
            "to the vector store."
        )

    def _load_pdf_from_bytes(self, file_bytes: bytes) -> list[LangChainDocument]:
        """Loads a PDF from raw bytes and extracts its text."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()

        return documents

    def _split_documents(
        self, documents: list[LangChainDocument]
    ) -> list[LangChainDocument]:
        """Splits a list of LangChain Documents into smaller chunks."""
        return self.text_splitter.split_documents(documents)
