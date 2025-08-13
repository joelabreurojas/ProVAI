import hashlib
import logging
import tempfile
from typing import Generator

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag.application.protocols import IngestionServiceProtocol

logger = logging.getLogger(__name__)


class IngestionService(IngestionServiceProtocol):
    def __init__(
        self,
        vector_store: Chroma,
        text_splitter: RecursiveCharacterTextSplitter,
        batch_size: int = 64,
    ):
        self.vector_store = vector_store
        self.text_splitter = text_splitter
        self.batch_size = batch_size

    def ingest_document(self, file_bytes: bytes, file_name: str, chat_id: int) -> None:
        """
        Processes a single PDF document, ensuring that only unique chunks
        from this document are upserted into the vector store.
        """
        logger.info(f"Starting batching ingestion for '{file_name}'...")
        total_chunks_ingested = 0

        # Create a generator that yields batches of chunks.
        chunk_batch_generator = self._batch_generator(
            self._page_chunk_generator(file_bytes, file_name, chat_id)
        )

        for chunk_batch in chunk_batch_generator:
            # De-duplicate chunks within the current batch
            unique_chunks_in_batch = list(
                {chunk.page_content: chunk for chunk in chunk_batch}.values()
            )

            if not unique_chunks_in_batch:
                continue

            ids = [self._generate_chunk_id(chunk) for chunk in unique_chunks_in_batch]
            self._store_chunks(unique_chunks_in_batch, ids)

            total_chunks_ingested += len(unique_chunks_in_batch)
            logger.info(
                f"Ingested batch of {len(unique_chunks_in_batch)} unique chunks..."
            )

        logger.info(
            "Completed ingestion for chat_id %d: %s -> %d unique chunks.",
            chat_id,
            file_name,
            total_chunks_ingested,
        )

    def _page_chunk_generator(
        self, file_bytes: bytes, file_name: str, chat_id: int
    ) -> Generator[Document, None, None]:
        """
        A generator that loads a PDF page by page, splits each page into
        chunks, and yields each chunk one at a time.
        """
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf", mode="wb") as tmpf:
            tmpf.write(file_bytes)
            loader = PyMuPDFLoader(tmpf.name)

            # --- THIS IS THE FIX ---
            # We iterate through pages, loading only one at a time into memory.
            for page in loader.load():
                chunks = self.text_splitter.split_documents([page])
                for chunk in chunks:
                    chunk.metadata["chat_id"] = chat_id
                    chunk.metadata["source"] = file_name
                    yield chunk

    def _batch_generator(
        self, generator: Generator[Document, None, None]
    ) -> Generator[list[Document], None, None]:
        """Takes a generator and yields batches of a specific size."""
        batch = []
        for item in generator:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def _generate_chunk_id(self, chunk: Document) -> str:
        """Generates a deterministic ID for a chunk."""
        source = chunk.metadata.get("source", "unknown")
        unique_string = f"{source}-{chunk.page_content}"
        return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

    def _store_chunks(self, chunks: list[Document], ids: list[str]) -> None:
        """Stores a batch of chunks in the vector store."""
        self.vector_store.add_documents(chunks, ids=ids)
