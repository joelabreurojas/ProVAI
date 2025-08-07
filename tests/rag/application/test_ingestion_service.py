from unittest.mock import MagicMock, patch

from src.rag.application.services.ingestion_service import IngestionService

FAKE_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n..."


@patch("src.rag.application.services.ingestion_service.PyPDFLoader")
def test_ingestion_service_orchestration(MockPyPDFLoader: MagicMock) -> None:
    mock_vector_store = MagicMock()
    mock_loader_instance = MockPyPDFLoader.return_value

    # Simulate the loader returning two simple documents
    mock_loader_instance.load.return_value = [
        MagicMock(page_content="This is the first sentence.", metadata={}),
        MagicMock(page_content="This is the second sentence.", metadata={}),
    ]

    ingestion_service = IngestionService(vector_store=mock_vector_store)

    # Override the text splitter for predictable chunking in the test
    ingestion_service.text_splitter = MagicMock()
    ingestion_service.text_splitter.split_documents.return_value = [
        MagicMock(page_content="chunk 1", metadata={}),
        MagicMock(page_content="chunk 2", metadata={}),
        MagicMock(page_content="chunk 3", metadata={}),
    ]

    # Act
    ingestion_service.ingest_document(
        file_bytes=FAKE_PDF_BYTES,
        file_name="test.pdf",
        chat_id=123,
    )

    # Assert that the loader was called correctly
    MockPyPDFLoader.assert_called_once()
    mock_loader_instance.load.assert_called_once()

    # Assert that the splitter was called
    ingestion_service.text_splitter.split_documents.assert_called_once()

    # Assert that the chunks were stored in the vector store
    mock_vector_store.add_documents.assert_called_once()

    # Assert that metadata was correctly added to the chunks
    call_args, _ = mock_vector_store.add_documents.call_args
    chunks_sent_to_store = call_args[0]
    assert len(chunks_sent_to_store) == 3
    for chunk in chunks_sent_to_store:
        assert chunk.metadata["chat_id"] == 123
        assert chunk.metadata["source"] == "test.pdf"
