import hashlib
from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document as LangChainDocument
from pytest_mock import MockerFixture
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.rag.application.services import IngestionService
from src.core.application.exceptions import DatabaseError, PDFParsingError
from src.core.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
)

FAKE_PDF_BYTES = b"%PDF-1.4..."


def test_ingestion_new_document_and_new_chunks(mocker: MockerFixture) -> None:
    """
    Tests the "happy path": when a new document with all new chunks is ingested,
    it correctly orchestrates the creation of all records (metadata-only for chunks)
    and adds the chunk CONTENT to the vector store.
    """
    mock_db_session = mocker.MagicMock(spec=SQLAlchemySession)

    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)

    mocker.patch(
        "src.api.rag.application.services.ingestion_service.IngestionService._load_pdf_from_bytes",
        return_value=[LangChainDocument(page_content="some text")],
    )
    mock_text_splitter.split_documents.return_value = [
        LangChainDocument(page_content="unique chunk 1"),
        LangChainDocument(page_content="unique chunk 2"),
    ]

    mock_chunk_repo.get_existing_chunks_by_hashes.return_value = set()

    service = IngestionService(
        db=mock_db_session,
        vector_store=mock_vector_store,
        text_splitter=mock_text_splitter,
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
    )

    service.ingest_document(file_bytes=FAKE_PDF_BYTES, file_name="new_doc.pdf")

    # Assert Document interactions
    mock_doc_repo.create_document.assert_called_once_with(file_name="new_doc.pdf")

    # Assert Chunk interactions
    mock_chunk_repo.get_existing_chunks_by_hashes.assert_called_once()
    assert mock_chunk_repo.create_chunk.call_count == 2

    # Verify that the call to create_chunk does NOT include the content.
    first_chunk_hash = hashlib.sha256("unique chunk 1".encode("utf-8")).hexdigest()
    mock_chunk_repo.create_chunk.assert_any_call(content_hash=first_chunk_hash)

    # We can check the call args directly to be certain
    call_args, call_kwargs = mock_chunk_repo.create_chunk.call_args_list[0]
    assert "content" not in call_kwargs  # Content should NOT be passed to the repo

    # Assert linking and transaction
    assert mock_doc_repo.link_chunk_to_document.call_count == 2
    mock_db_session.commit.assert_called_once()

    # Assert that the CONTENT was passed to the VECTOR STORE
    mock_vector_store.add_texts.assert_called_once()
    texts_sent_to_vector_store = mock_vector_store.add_texts.call_args.kwargs["texts"]
    assert len(texts_sent_to_vector_store) == 2
    assert "unique chunk 1" in texts_sent_to_vector_store
    assert "unique chunk 2" in texts_sent_to_vector_store


def test_ingestion_new_document_with_existing_chunks(mocker: MockerFixture) -> None:
    """
    Tests the de-duplication path: a document with an existing chunk is ingested.
    """
    mock_db_session = mocker.MagicMock(spec=SQLAlchemySession)
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)

    mocker.patch(
        "src.api.rag.application.services.ingestion_service.IngestionService._load_pdf_from_bytes",
        return_value=[LangChainDocument(page_content="some text")],
    )
    chunk_content = "this chunk already exists"
    mock_text_splitter.split_documents.return_value = [
        LangChainDocument(page_content=chunk_content)
    ]
    expected_hash = hashlib.sha256(chunk_content.encode("utf-8")).hexdigest()
    mock_chunk_repo.get_existing_chunks_by_hashes.return_value = {expected_hash}
    mock_existing_chunk_db_object = MagicMock()
    mock_chunk_repo.get_chunk_by_hash.return_value = mock_existing_chunk_db_object

    service = IngestionService(
        db=mock_db_session,
        vector_store=mock_vector_store,
        text_splitter=mock_text_splitter,
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
    )

    service.ingest_document(file_bytes=FAKE_PDF_BYTES, file_name="another_doc.pdf")

    mock_doc_repo.create_document.assert_called_once()
    mock_chunk_repo.get_chunk_by_hash.assert_called_once_with(expected_hash)
    mock_chunk_repo.create_chunk.assert_not_called()
    mock_vector_store.add_texts.assert_not_called()
    mock_doc_repo.link_chunk_to_document.assert_called_once_with(
        mocker.ANY,
        mock_existing_chunk_db_object,
    )
    mock_db_session.commit.assert_called_once()


def test_ingestion_fails_gracefully_on_pdf_parsing_error(mocker: MockerFixture) -> None:
    """
    Tests that if the underlying PDF parsing library fails, the IngestionService
    catches the error and raises a specific PDFParsingError.
    """
    mock_db_session = mocker.MagicMock(spec=SQLAlchemySession)
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)

    # Simulate the `fitz.open` call raising a generic RuntimeError,
    # which is what it does for corrupt files.
    mocker.patch(
        "src.api.rag.application.services.ingestion_service.fitz.open",
        side_effect=RuntimeError("This is a simulated parsing error"),
    )

    service = IngestionService(
        db=mock_db_session,
        vector_store=mock_vector_store,
        text_splitter=mock_text_splitter,
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
    )

    with pytest.raises(PDFParsingError):
        service.ingest_document(
            file_bytes=b"these are corrupted bytes", file_name="corrupt.pdf"
        )

    # Crucially, assert that no database changes were attempted or committed.
    mock_doc_repo.create_document.assert_not_called()
    mock_chunk_repo.create_chunk.assert_not_called()
    mock_vector_store.add_texts.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_ingestion_rolls_back_transaction_on_database_error(
    mocker: MockerFixture,
) -> None:
    """
    Tests that if a database error occurs during the commit phase, the service
    catches it, rolls back the transaction, and raises a specific DatabaseError.
    """
    mock_db_session = mocker.MagicMock(spec=SQLAlchemySession)
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)

    # Simulate a successful PDF parse
    mocker.patch(
        "src.api.rag.application.services.ingestion_service.IngestionService._load_pdf_from_bytes",
        return_value=[LangChainDocument(page_content="some text")],
    )
    mock_text_splitter.split_documents.return_value = [
        LangChainDocument(page_content="a valid chunk")
    ]
    mock_chunk_repo.get_existing_chunks_by_hashes.return_value = set()

    # Make the `commit` call fail.
    mock_db_session.commit.side_effect = SQLAlchemyError(
        "Simulated DB connection error"
    )

    service = IngestionService(
        db=mock_db_session,
        vector_store=mock_vector_store,
        text_splitter=mock_text_splitter,
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
    )

    with pytest.raises(DatabaseError):
        service.ingest_document(file_bytes=FAKE_PDF_BYTES, file_name="db_fail.pdf")

    mock_doc_repo.create_document.assert_called_once()
    mock_chunk_repo.create_chunk.assert_called_once()
    mock_vector_store.add_texts.assert_called_once()

    # Crucially, assert that a rollback was issued after the commit failed.
    mock_db_session.commit.assert_called_once()
    mock_db_session.rollback.assert_called_once()
