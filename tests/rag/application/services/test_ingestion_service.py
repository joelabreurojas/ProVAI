from pytest_mock import MockerFixture

from langchain_core.documents import Document
from src.chat.application.protocols import ContentRepositoryProtocol
from src.rag.application.services.ingestion_service import IngestionService


def test_ingestion_new_document_new_chunks(mocker: MockerFixture) -> None:
    """
    Tests that when a new document with all new chunks is ingested,
    the service correctly calls its dependencies and adds chunks to the vector store.
    """
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_content_repo = mocker.MagicMock(spec=ContentRepositoryProtocol)

    # Simulate that all chunks are new
    mock_content_repo.get_chunk_by_hash.return_value = None

    service = IngestionService(mock_vector_store, mock_text_splitter, mock_content_repo)

    # Mock the internal helper methods of the service we are testing.
    # We are not testing PDF parsing, only the orchestration.
    mock_langchain_docs = [Document(page_content="fake doc content")]
    mock_chunks = [Document(page_content="fake chunk content")]

    mocker.patch.object(
        service, "_load_pdf_from_bytes", return_value=mock_langchain_docs
    )
    mocker.patch.object(service, "_split_documents", return_value=mock_chunks)

    service.ingest_document(b"any pdf bytes", "doc.pdf", 1)

    service._load_pdf_from_bytes.assert_called_once_with(b"any pdf bytes")
    service._split_documents.assert_called_once_with(mock_langchain_docs)

    mock_content_repo.create_document.assert_called_once()
    mock_content_repo.create_chunk.assert_called_once()
    mock_content_repo.link_chunk_to_document.assert_called_once()
    mock_vector_store.add_texts.assert_called_once()


def test_ingestion_document_with_existing_chunks(mocker: MockerFixture) -> None:
    """
    Tests that when a document with existing chunks is ingested, the service
    correctly links them and does NOT add them to the vector store again.
    """
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()
    mock_content_repo = mocker.MagicMock(spec=ContentRepositoryProtocol)

    # Simulate that all chunks already exist in the DB
    mock_content_repo.get_chunk_by_hash.return_value = mocker.MagicMock()

    service = IngestionService(mock_vector_store, mock_text_splitter, mock_content_repo)

    # Mock the internal helpers here as well.
    mocker.patch.object(service, "_load_pdf_from_bytes", return_value=[])
    mocker.patch.object(
        service,
        "_split_documents",
        return_value=[Document(page_content="existing chunk")],
    )

    service.ingest_document(b"any pdf bytes", "doc.pdf", 1)

    mock_content_repo.create_document.assert_called_once()
    # It should NEVER try to create a new chunk record
    mock_content_repo.create_chunk.assert_not_called()
    # It should NEVER try to add texts to the vector store
    mock_vector_store.add_texts.assert_not_called()
    # It should still link the existing chunk to the new document
    mock_content_repo.link_chunk_to_document.assert_called_once()
