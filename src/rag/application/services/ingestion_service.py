import hashlib
import logging

import fitz
from langchain_chroma import Chroma
from langchain_core.documents import Document as LangChainDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.application.exceptions import DatabaseError
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
from src.tutor.application.exceptions import TutorNotFoundError
from src.tutor.application.protocols import TutorRepositoryProtocol

logger = logging.getLogger(__name__)


class IngestionService(IngestionServiceProtocol):
    """
    Orchestrates the document ingestion pipeline. This service is responsible for
    processing a document, ensuring its content is stored idempotently,
    and linking it to the correct tutor in a single, atomic transaction.
    """

    def __init__(
        self,
        db: SQLAlchemySession,
        vector_store: Chroma,
        text_splitter: RecursiveCharacterTextSplitter,
        doc_repo: DocumentRepositoryProtocol,
        chunk_repo: ChunkRepositoryProtocol,
        tutor_repo: TutorRepositoryProtocol,
    ):
        self.db = db
        self.vector_store = vector_store
        self.text_splitter = text_splitter
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.tutor_repo = tutor_repo

    def ingest_document(self, file_bytes: bytes, file_name: str, tutor_id: int) -> None:
        """
        Processes a PDF, creating relational records for documents and chunks,
        and storing embeddings in the vector store. This process is idempotent.
        """
        tutor = self.tutor_repo.get_tutor_by_id(tutor_id)
        if not tutor:
            raise TutorNotFoundError(tutor_id=tutor_id)

        try:
            langchain_docs = self._load_pdf_from_bytes(file_bytes)
        except RuntimeError as e:
            logger.error(f"PDF parsing failed for document {file_name}: {e}")
            raise PDFParsingError() from e

        try:
            db_document = self.doc_repo.create_document(file_name=file_name)
            self.tutor_repo.link_document_to_tutor(tutor, db_document)

            chunks = self._split_documents(langchain_docs)

            all_hashes = [
                hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest()
                for chunk in chunks
            ]
            existing_hashes = self.chunk_repo.get_existing_chunks_by_hashes(all_hashes)

            new_chunks_for_vector_store = []
            new_chunk_ids_for_vector_store = []

            for i, chunk_doc in enumerate(chunks):
                content_hash = all_hashes[i]

                db_chunk: Chunk | None = None

                if content_hash not in existing_hashes:
                    db_chunk = self.chunk_repo.create_chunk(content_hash=content_hash)
                    new_chunks_for_vector_store.append(chunk_doc.page_content)
                    new_chunk_ids_for_vector_store.append(content_hash)
                else:
                    db_chunk = self.chunk_repo.get_chunk_by_hash(content_hash)

                if db_chunk:
                    self.doc_repo.link_chunk_to_document(db_document, db_chunk)
                else:
                    logger.warning(
                        f"Failed to create chunk for content hash {content_hash}"
                    )

            if new_chunks_for_vector_store:
                self.vector_store.add_texts(
                    texts=new_chunks_for_vector_store,
                    ids=new_chunk_ids_for_vector_store,
                )

            self.db.commit()

            logger.info(
                f"Successfully ingested '{file_name}' for tutor_id {tutor_id}. "
                f"Added {len(new_chunks_for_vector_store)} new unique chunks \
                to the vector store."
            )

        except RuntimeError as e:
            logger.error(f"PDF parsing failed for {file_name}: {e}")
            self.db.rollback()
            raise PDFParsingError() from e

        except SQLAlchemyError as e:
            logger.error(f"Database error during ingestion for {file_name}: {e}")
            self.db.rollback()
            raise DatabaseError() from e

        except Exception as e:
            logger.error(
                f"An unexpected error occurred during ingestion for {file_name}: {e}"
            )
            self.db.rollback()
            raise IngestionError() from e

    def _load_pdf_from_bytes(self, file_bytes: bytes) -> list[LangChainDocument]:
        """Loads a PDF from in-memory bytes using PyMuPDF."""
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            full_text = "".join(page.get_text("text") for page in doc)
            if not full_text:
                logger.warning("PDF parsing with PyMuPDF resulted in empty text.")
                return []
            return [LangChainDocument(page_content=full_text)]

    def _split_documents(
        self, documents: list[LangChainDocument]
    ) -> list[LangChainDocument]:
        """Splits loaded documents into smaller chunks."""
        return self.text_splitter.split_documents(documents)
