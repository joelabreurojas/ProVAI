import hashlib
import logging
import tempfile

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document as LangChainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session as SQLAlchemySession

from src.chat.application.exceptions import ChatNotFoundError
from src.chat.application.protocols import ChatRepositoryProtocol
from src.rag.application.exceptions import (
    IngestionError,
    PDFParsingError,
)
from src.rag.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    IngestionServiceProtocol,
)
from src.rag.domain.models import Chunk

logger = logging.getLogger(__name__)


class IngestionService(IngestionServiceProtocol):
    """
    Orchestrates the document ingestion pipeline. This service is responsible for
    processing a document, ensuring its content is stored idempotently,
    and linking it to the correct chat in a single, atomic transaction.
    """

    def __init__(
        self,
        db: SQLAlchemySession,
        vector_store: Chroma,
        text_splitter: RecursiveCharacterTextSplitter,
        doc_repo: DocumentRepositoryProtocol,
        chunk_repo: ChunkRepositoryProtocol,
        chat_repo: ChatRepositoryProtocol,
    ):
        self.db = db
        self.vector_store = vector_store
        self.text_splitter = text_splitter
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.chat_repo = chat_repo

    def ingest_document(self, file_bytes: bytes, file_name: str, chat_id: int) -> None:
        """
        Processes a PDF, creating relational records for documents and chunks,
        and storing embeddings in the vector store. This process is idempotent.
        """
        chat = self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise ChatNotFoundError(chat_id=chat_id)

        db_document = self.doc_repo.create_document(file_name=file_name)
        self.chat_repo.link_document_to_chat(chat, db_document)

        try:
            langchain_docs = self._load_pdf_from_bytes(file_bytes)
        except Exception as e:
            logger.error(f"PDF parsing failed for document {file_name}: {e}")
            raise PDFParsingError() from e

        chunks = self._split_documents(langchain_docs)

        all_hashes = [
            hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest()
            for chunk in chunks
        ]

        existing_hashes = self.chunk_repo.get_existing_chunks_by_hashes(all_hashes)

        chunks_to_add_to_vector_store = []
        chunk_ids_for_vector_store = []

        try:
            for i, chunk_doc in enumerate(chunks):
                content_hash = all_hashes[i]

                db_chunk: Chunk | None = None

                if content_hash not in existing_hashes:
                    db_chunk = self.chunk_repo.create_chunk(content_hash=content_hash)

                    chunks_to_add_to_vector_store.append(chunk_doc.page_content)
                    chunk_ids_for_vector_store.append(content_hash)
                else:
                    db_chunk = self.chunk_repo.get_chunk_by_hash(content_hash)

                if db_chunk:
                    self.doc_repo.link_chunk_to_document(db_document, db_chunk)
                else:
                    logger.warning(
                        "Could not find or create a DB record for chunk hash %s",
                        content_hash,
                    )

            self.db.commit()

            # The vector store addition happens AFTER the main transaction succeeds.
            if chunks_to_add_to_vector_store:
                self.vector_store.add_texts(
                    texts=chunks_to_add_to_vector_store, ids=chunk_ids_for_vector_store
                )

        except Exception as e:
            logger.error(f"Ingestion failed for document {file_name}: {e}")
            self.db.rollback()
            raise IngestionError() from e

        logger.info(
            f"Successfully ingested '{file_name}' for chat_id {chat_id}. "
            f"Added {len(chunks_to_add_to_vector_store)} new unique chunks "
            "to the vector store."
        )

    def _load_pdf_from_bytes(self, file_bytes: bytes) -> list[LangChainDocument]:
        """Loads a PDF from in-memory bytes by writing to a temporary file."""
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()

            loader = PyPDFLoader(file_path=temp_file.name)
            documents: list[LangChainDocument] = loader.load()

            return documents

    def _split_documents(
        self, documents: list[LangChainDocument]
    ) -> list[LangChainDocument]:
        """Splits loaded documents into smaller chunks."""
        chunks: list[LangChainDocument] = self.text_splitter.split_documents(documents)

        return chunks
