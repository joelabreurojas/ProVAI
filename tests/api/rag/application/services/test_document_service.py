from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from src.api.rag.application.services import DocumentService
from src.core.application.protocols import (
    ChunkRepositoryProtocol,
    DocumentRepositoryProtocol,
    TutorRepositoryProtocol,
)
from src.core.domain.models import Document, Tutor


def test_delete_document_garbage_collects_orphans(mocker: MockerFixture) -> None:
    """
    Tests that when a document is fully unlinked, its orphaned chunks are
    deleted from both the relational DB and the vector store.
    """
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)
    mock_tutor_repo = mocker.MagicMock(spec=TutorRepositoryProtocol)
    mock_vector_store = mocker.MagicMock()

    mock_tutor = mocker.MagicMock()
    mock_tutor_repo.get_tutor_by_id.return_value = mock_tutor

    mock_document = mocker.MagicMock()
    mock_document.configure_mock(tutors=[])  # Will be updated by side effect
    mock_doc_repo.get_document_by_id.return_value = mock_document

    def remove_link_side_effect(tutor: MagicMock, doc: MagicMock) -> None:
        doc.tutors = []  # Simulate the document is now unlinked

    mock_tutor_repo.remove_document_from_tutor.side_effect = remove_link_side_effect

    mock_orphan_chunk = mocker.MagicMock(content_hash="unique_hash_123")
    mock_chunk_repo.get_orphaned_chunks.return_value = [mock_orphan_chunk]

    service = DocumentService(
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
        tutor_repo=mock_tutor_repo,
        vector_store=mock_vector_store,
    )

    service.delete_document_from_tutor(document_id=1, tutor_id=1)

    mock_tutor_repo.remove_document_from_tutor.assert_called_once_with(
        mock_tutor, mock_document
    )
    mock_chunk_repo.get_orphaned_chunks.assert_called_once_with(mock_document)
    mock_doc_repo.delete_document.assert_called_once_with(mock_document)
    mock_chunk_repo.delete_chunks.assert_called_once_with([mock_orphan_chunk])
    mock_vector_store.delete.assert_called_once_with(ids=["unique_hash_123"])


def test_delete_shared_document_does_not_garbage_collect(mocker: MockerFixture) -> None:
    """
    Tests that when a document is removed from one tutor but is still linked
    to another, no garbage collection is performed.
    """
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)
    mock_tutor_repo = mocker.MagicMock(spec=TutorRepositoryProtocol)
    mock_vector_store = mocker.MagicMock()

    mock_tutor = mocker.MagicMock()
    mock_tutor_repo.get_tutor_by_id.return_value = mock_tutor

    # Simulate that the document is still linked to another tutor
    mock_document = mocker.MagicMock(tutors=[mocker.MagicMock()])
    mock_doc_repo.get_document_by_id.return_value = mock_document

    service = DocumentService(
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
        tutor_repo=mock_tutor_repo,
        vector_store=mock_vector_store,
    )

    service.delete_document_from_tutor(document_id=1, tutor_id=1)

    mock_tutor_repo.remove_document_from_tutor.assert_called_once()

    # Because the document was still linked, NONE of the deletion methods should fire.
    mock_chunk_repo.get_orphaned_chunks.assert_not_called()
    mock_doc_repo.delete_document.assert_not_called()
    mock_chunk_repo.delete_chunks.assert_not_called()
    mock_vector_store.delete.assert_not_called()


def test_deleting_document_from_one_tutor_does_not_affect_shared_document(
    mocker: MockerFixture,
) -> None:
    """
    Tests the "shared document" scenario. When a document is unlinked from one
    tutor but still in use by another, it should NOT be deleted, and its
    chunks should NOT be garbage collected.
    """
    mock_doc_repo = mocker.MagicMock(spec=DocumentRepositoryProtocol)
    mock_chunk_repo = mocker.MagicMock(spec=ChunkRepositoryProtocol)
    mock_tutor_repo = mocker.MagicMock(spec=TutorRepositoryProtocol)
    mock_vector_store = mocker.MagicMock()

    # Simulate the tutor from which we are deleting the document
    mock_tutor_A = mocker.MagicMock(spec=Tutor, id=1)
    # Simulate ANOTHER tutor that also uses this document
    mock_tutor_B = mocker.MagicMock(spec=Tutor, id=2)

    # This document is linked to TWO tutors
    mock_shared_document = mocker.MagicMock(
        spec=Document, id=99, tutors=[mock_tutor_A, mock_tutor_B]
    )

    mock_tutor_repo.get_tutor_by_id.return_value = mock_tutor_A
    mock_doc_repo.get_document_by_id.return_value = mock_shared_document

    # When the repository's `remove_document_from_tutor`
    # is called, we simulate the database state AFTER the link is removed.
    # The document is no longer linked to Tutor A, but it IS still linked to Tutor B.
    def remove_link_side_effect(tutor: Tutor, doc: Document) -> None:
        # We manually update the mock's internal state to reflect the change.
        doc.tutors = [mock_tutor_B]

    mock_tutor_repo.remove_document_from_tutor.side_effect = remove_link_side_effect

    service = DocumentService(
        doc_repo=mock_doc_repo,
        chunk_repo=mock_chunk_repo,
        tutor_repo=mock_tutor_repo,
        vector_store=mock_vector_store,
    )

    # Delete the document from Tutor A
    service.delete_document_from_tutor(document_id=99, tutor_id=1)

    mock_tutor_repo.remove_document_from_tutor.assert_called_once_with(
        mock_tutor_A, mock_shared_document
    )

    mock_doc_repo.delete_document.assert_not_called()
    mock_chunk_repo.get_orphaned_chunks.assert_not_called()
    mock_chunk_repo.delete_chunks.assert_not_called()
    mock_vector_store.delete.assert_not_called()
