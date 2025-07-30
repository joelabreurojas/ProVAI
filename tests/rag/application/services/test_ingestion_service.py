from langchain_core.documents import Document
from pytest_mock import MockerFixture

from src.rag.application.services.ingestion_service import IngestionService

FAKE_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n..."


def test_ingestion_service_orchestrates_pipeline_correctly(
    mocker: MockerFixture,
) -> None:
    """
    Verify that the `ingest_document` method correctly orchestrates the
    full pipeline: loading a PDF, splitting it into chunks, adding the
    correct metadata, and storing the final chunks in the vector store.
    """
    mock_vector_store = mocker.MagicMock()
    mock_text_splitter = mocker.MagicMock()

    # Use mocker.patch to replace the PyPDFLoader class within the service's module
    mock_pdf_loader_class = mocker.patch(
        "src.rag.application.services.ingestion_service.PyPDFLoader"
    )
    mock_loader_instance = mock_pdf_loader_class.return_value
    mock_loader_instance.load.return_value = [
        Document(page_content="Raw text.", metadata={})
    ]

    expected_chunks = [
        Document(page_content="chunk 1", metadata={}),
        Document(page_content="chunk 2", metadata={}),
    ]
    mock_text_splitter.split_documents.return_value = expected_chunks

    # Pass the new mock dependency into the constructor
    ingestion_service = IngestionService(
        vector_store=mock_vector_store, text_splitter=mock_text_splitter
    )

    ingestion_service.ingest_document(
        file_bytes=FAKE_PDF_BYTES, file_name="test.pdf", chat_id=123
    )

    mock_text_splitter.split_documents.assert_called_once()
    mock_vector_store.add_documents.assert_called_once()

    call_args, _ = mock_vector_store.add_documents.call_args
    chunks_sent_to_store = call_args[0]

    assert len(chunks_sent_to_store) == 2

    for chunk in chunks_sent_to_store:
        assert chunk.metadata["chat_id"] == 123
        assert chunk.metadata["source"] == "test.pdf"
