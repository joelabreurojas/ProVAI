import logging
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates the document ingestion pipeline."""

    def __init__(self, vector_store: Chroma):
        self.vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=300,
            chunk_overlap=0,
            encoding_name="cl100k_base",
        )

    def ingest_document(self, file_bytes: bytes, file_name: str, chat_id: int) -> None:
        """Processes a single PDF document and stores it in the vector store."""
        documents = self._load_pdf_from_bytes(file_bytes)
        chunks = self._split_documents(documents)

        for chunk in chunks:
            chunk.metadata["chat_id"] = chat_id
            chunk.metadata["source"] = file_name

        self._store_chunks(chunks)
        logger.info(
            f"Ingested '{file_name}' into {len(chunks)} chunks for chat_id {chat_id}."
        )

    def _load_pdf_from_bytes(self, file_bytes: bytes) -> list[Document]:
        """Loads a PDF from in-memory bytes by writing to a temporary file."""
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()  # Ensure all bytes are written to disk

            loader = PyPDFLoader(file_path=temp_file.name)
            return loader.load()

    def _split_documents(self, documents: list[Document]) -> list[Document]:
        """Splits loaded documents into smaller chunks."""
        return self.text_splitter.split_documents(documents)

    def _store_chunks(self, chunks: list[Document]) -> None:
        """Stores the document chunks in the Chroma vector store."""
        self.vector_store.add_documents(chunks)
