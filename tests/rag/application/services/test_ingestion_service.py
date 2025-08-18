import hashlib

from langchain_core.documents import Document as LangChainDocument
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from src.chat.application.protocols import ChatRepositoryProtocol
from src.rag.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
)
from src.rag.application.services import IngestionService

FAKE_PDF_BYTES = b"%PDF-1.4..."


def test_ingestion_new_document_and_new_chunks(mocker: MockerFixture) -> None:
    """
    Tests the "happy path": when a new document with all new chunks is ingested,
    it correctly orchestrates the creation of all records and adds the chunks
    to the vector store.
    """
    mock_db_session = mocker.MagicMock(spec=Session)
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)

    mocker.patch(
        "src.rag.application.services.ingestion_service.IngestionService._load_pdf_from_bytes",
        return_value=[LangChainDocument(page_content="some text")],
    )
    # Simulate the text splitter returning two unique chunks
    mock_text_splitter.split_documents.return_value = [
        LangChainDocument(page_content="unique chunk 1"),
        LangChainDocument(page_content="unique chunk 2"),
    ]

    # Simulate that no chunks currently exist in the database
    mock_chunk_repo.get_existing_chunks_by_hashes.return_value = set()

    service = IngestionService(
        db=mock_db_session,
        vector_store=mock_vector_store,
        text_splitter=mock_text_splitter,
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
        chat_repo=mock_chat_repo,
    )

    service.ingest_document(
        file_bytes=FAKE_PDF_BYTES, file_name="new_doc.pdf", chat_id=1
    )

    mock_doc_repo.create_document.assert_called_once_with(file_name="new_doc.pdf")
    mock_chat_repo.link_document_to_chat.assert_called_once()
    mock_chunk_repo.get_existing_chunks_by_hashes.assert_called_once()
    # It should have created a new DB record for each of the 2 chunks
    assert mock_chunk_repo.create_chunk.call_count == 2
    # It should have linked each of the 2 chunks to the new document
    assert mock_doc_repo.link_chunk_to_document.call_count == 2
    mock_db_session.commit.assert_called_once()
    # It should have added the 2 new chunks to the vector store
    mock_vector_store.add_texts.assert_called_once()
    assert len(mock_vector_store.add_texts.call_args.kwargs["texts"]) == 2


def test_ingestion_new_document_with_existing_chunks(mocker: MockerFixture) -> None:
    """
    Tests the de-duplication path: when a document contains a chunk that
    already exists, the service correctly links it and does NOT add it
    to the vector store again.
    """
    mock_db_session = mocker.MagicMock(spec=Session)
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)

    mocker.patch(
        "src.rag.application.services.ingestion_service.IngestionService._load_pdf_from_bytes",
        return_value=[LangChainDocument(page_content="some text")],
    )
    chunk_content = "this chunk already exists"
    mock_text_splitter.split_documents.return_value = [
        LangChainDocument(page_content=chunk_content)
    ]

    # Calculate the hash that our service will generate
    expected_hash = hashlib.sha256(chunk_content.encode("utf-8")).hexdigest()

    # Simulate that this hash already exists in our database
    mock_chunk_repo.get_existing_chunks_by_hashes.return_value = {expected_hash}

    mock_existing_chunk_db_object = mocker.MagicMock()
    mock_chunk_repo.get_chunk_by_hash.return_value = mock_existing_chunk_db_object

    service = IngestionService(
        db=mock_db_session,
        vector_store=mock_vector_store,
        text_splitter=mock_text_splitter,
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
        chat_repo=mock_chat_repo,
    )

    service.ingest_document(
        file_bytes=FAKE_PDF_BYTES, file_name="another_doc.pdf", chat_id=1
    )

    mock_doc_repo.create_document.assert_called_once()
    mock_chat_repo.link_document_to_chat.assert_called_once()
    mock_chunk_repo.get_chunk_by_hash.assert_called_once_with(expected_hash)

    # It should NEVER try to create a new chunk record in the DB
    mock_chunk_repo.create_chunk.assert_not_called()
    # It should NEVER try to add texts to the vector store
    mock_vector_store.add_texts.assert_not_called()

    # It should still link the EXISTING chunk to the new document
    mock_doc_repo.link_chunk_to_document.assert_called_once_with(
        mocker.ANY,  # The newly created document object
        mock_existing_chunk_db_object,
    )
    mock_db_session.commit.assert_called_once()
