from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.api.chat.application.services import ChatService
from src.core.application.exceptions import ChatNotFoundError, UserNotEnrolledError
from src.core.application.protocols import (
    ChatRepositoryProtocol,
    IngestionServiceProtocol,
    RAGServiceProtocol,
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.core.domain.models import Chat, Document, Message, Tutor, User


def create_mocked_chat_service(
    mocker: MockerFixture,
) -> tuple[ChatService, dict[str, MagicMock]]:
    """Creates a ChatService with all its dependencies mocked."""
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)
    mock_tutor_service = mocker.MagicMock(spec=TutorServiceProtocol)
    mock_rag_service = mocker.MagicMock(spec=RAGServiceProtocol)
    mock_ingestion_service = mocker.MagicMock(spec=IngestionServiceProtocol)
    mock_tutor_repo = mocker.MagicMock(spec=TutorRepositoryProtocol)

    service = ChatService(
        chat_repo=mock_chat_repo,
        tutor_service=mock_tutor_service,
        rag_service=mock_rag_service,
        ingestion_service=mock_ingestion_service,
        tutor_repo=mock_tutor_repo,
    )

    mocks = {
        "chat_repo": mock_chat_repo,
        "tutor_service": mock_tutor_service,
        "rag_service": mock_rag_service,
        "ingestion_service": mock_ingestion_service,
        "tutor_repo": mock_tutor_repo,
    }
    return service, mocks


def test_create_new_chat_successfully(mocker: MockerFixture) -> None:
    """Tests that the service authorizes the user before creating a chat."""
    service, mocks = create_mocked_chat_service(mocker)
    mock_user = mocker.MagicMock(spec=User, id=101)
    tutor_id = 1
    title = "New Study Chat"

    service.create_new_chat(tutor_id=tutor_id, user=mock_user, title=title)

    mocks["tutor_service"].verify_user_can_access_tutor.assert_called_once_with(
        tutor_id, mock_user
    )
    mocks["chat_repo"].create_chat.assert_called_once_with(
        tutor_id=tutor_id, user_id=mock_user.id, title=title
    )


def test_get_chat_returns_chat_after_authorization(mocker: MockerFixture) -> None:
    """Tests that the service returns a chat object after authorizing the user."""
    service, mocks = create_mocked_chat_service(mocker)
    mock_user = mocker.MagicMock(spec=User)
    mock_chat = mocker.MagicMock(spec=Chat, tutor_id=1)
    mocks["chat_repo"].get_chat_by_id.return_value = mock_chat
    chat_id = 5

    result = service.get_chat(chat_id=chat_id, user=mock_user)

    mocks["chat_repo"].get_chat_by_id.assert_called_once_with(chat_id=chat_id)
    mocks["tutor_service"].verify_user_can_access_tutor.assert_called_once_with(
        mock_chat.tutor_id, mock_user
    )
    assert result is mock_chat


def test_get_chat_raises_error_when_not_found(mocker: MockerFixture) -> None:
    """
    Tests that a ChatNotFoundError is raised if the repository does not find
    the chat, and that no authorization check is performed.
    """
    service, mocks = create_mocked_chat_service(mocker)
    mocks["chat_repo"].get_chat_by_id.return_value = None
    mock_user = mocker.MagicMock(spec=User)

    with pytest.raises(ChatNotFoundError):
        service.get_chat(chat_id=999, user=mock_user)

    mocks["chat_repo"].get_chat_by_id.assert_called_once_with(chat_id=999)
    mocks["tutor_service"].verify_user_can_access_tutor.assert_not_called()


def test_get_chats_for_user_and_tutor(mocker: MockerFixture) -> None:
    """
    Tests that the service authorizes the user, fetches all their chats,
    and correctly filters them for the specified tutor.
    """
    service, mocks = create_mocked_chat_service(mocker)
    mock_user = mocker.MagicMock(spec=User, id=101)
    tutor_id = 1

    # Simulate the repository returning chats from MULTIPLE tutors
    chat_for_tutor1 = mocker.MagicMock(spec=Chat, tutor_id=1)
    chat_for_tutor2 = mocker.MagicMock(spec=Chat, tutor_id=2)
    chat2_for_tutor1 = mocker.MagicMock(spec=Chat, tutor_id=1)
    mocks["chat_repo"].get_chats_for_user.return_value = [
        chat_for_tutor1,
        chat_for_tutor2,
        chat2_for_tutor1,
    ]

    result = service.get_chats_for_user_and_tutor(tutor_id=tutor_id, user=mock_user)

    # Verify the orchestration
    mocks["tutor_service"].verify_user_can_access_tutor.assert_called_once_with(
        tutor_id, mock_user
    )
    mocks["chat_repo"].get_chats_for_user.assert_called_once_with(user_id=mock_user.id)

    # Verify the filtering logic
    assert len(result) == 2
    assert chat_for_tutor1 in result
    assert chat2_for_tutor1 in result
    assert chat_for_tutor2 not in result


def test_add_document_to_chat_orchestration(mocker: MockerFixture) -> None:
    """
    Tests the full orchestration logic for adding a document to a chat.
    """
    service, mocks = create_mocked_chat_service(mocker)
    mock_user = mocker.MagicMock(spec=User)
    mock_chat = mocker.MagicMock(spec=Chat, tutor_id=1)
    mock_tutor = mocker.MagicMock(spec=Tutor, id=1)
    mock_document = mocker.MagicMock(spec=Document)

    # Setup the return values for the mocked calls
    mocks["chat_repo"].get_chat_by_id.return_value = mock_chat
    mocks["tutor_service"].get_tutor.return_value = mock_tutor
    mocks["ingestion_service"].ingest_document.return_value = mock_document

    file_bytes = b"test pdf"
    file_name = "test.pdf"

    service.add_document_to_chat(
        chat_id=5,
        file_bytes=file_bytes,
        file_name=file_name,
        current_user=mock_user,
    )

    # Verify the orchestration sequence
    mocks["chat_repo"].get_chat_by_id.assert_called_once_with(chat_id=5)
    mocks["tutor_service"].verify_user_is_tutor_owner.assert_called_once_with(
        mock_tutor.id, mock_user
    )
    mocks["ingestion_service"].ingest_document.assert_called_once_with(
        file_bytes, file_name
    )
    mocks["tutor_repo"].link_document_to_tutor.assert_called_once_with(
        mock_tutor, mock_document
    )


def test_post_message_orchestration(mocker: MockerFixture) -> None:
    """
    Tests the full orchestration logic for posting a message and getting a RAG response.
    """
    service, mocks = create_mocked_chat_service(mocker)
    mock_user = mocker.MagicMock(spec=User)
    mock_chat = mocker.MagicMock(spec=Chat, tutor_id=1)
    query = "What is RAG?"
    expected_answer = "RAG is..."
    valid_hashes = ["hash1", "hash2"]

    mocks["chat_repo"].get_chat_by_id.return_value = mock_chat
    mocks["tutor_repo"].get_chunk_hashes_for_tutor.return_value = valid_hashes
    mocks["rag_service"].answer_query.return_value = expected_answer

    answer = service.post_message(chat_id=5, query=query, current_user=mock_user)

    # Verify the orchestration sequence
    mocks["chat_repo"].get_chat_by_id.assert_called_once_with(chat_id=5)
    mocks["tutor_service"].verify_user_can_access_tutor.assert_called_once_with(
        mock_chat.tutor_id, mock_user
    )
    mocks["tutor_repo"].get_chunk_hashes_for_tutor.assert_called_once_with(
        mock_chat.tutor_id
    )
    mocks["rag_service"].answer_query.assert_called_once_with(
        query, {"content_hash": {"$in": valid_hashes}}
    )
    assert mocks["chat_repo"].add_message.call_count == 2
    mocks["chat_repo"].add_message.assert_any_call(
        chat_id=5, role="user", content=query
    )
    mocks["chat_repo"].add_message.assert_any_call(
        chat_id=5, role="tutor", content=expected_answer
    )
    assert answer == expected_answer


def test_get_history_authorizes_and_returns_sorted(mocker: MockerFixture) -> None:
    """
    Tests that get_history authorizes the user before returning sorted messages.
    """
    service, mocks = create_mocked_chat_service(mocker)
    mock_user = mocker.MagicMock(spec=User)

    msg1 = mocker.MagicMock(spec=Message, timestamp="2025-01-01T12:00:00")
    msg3 = mocker.MagicMock(spec=Message, timestamp="2025-01-01T12:02:00")
    msg2 = mocker.MagicMock(spec=Message, timestamp="2025-01-01T12:01:00")

    mock_chat = mocker.MagicMock(spec=Chat, tutor_id=1, messages=[msg1, msg3, msg2])
    mocks["chat_repo"].get_chat_by_id.return_value = mock_chat

    result = service.get_history(chat_id=5, user=mock_user)

    mocks["chat_repo"].get_chat_by_id.assert_called_once_with(chat_id=5)
    mocks["tutor_service"].verify_user_can_access_tutor.assert_called_once_with(
        mock_chat.tutor_id, mock_user
    )
    assert result == [msg1, msg2, msg3]  # Verifies sorting


def test_post_message_fails_if_user_not_enrolled(mocker: MockerFixture) -> None:
    """
    Tests that a user cannot post a message to a chat if they are not
    enrolled in the parent tutor.
    """
    service, mocks = create_mocked_chat_service(mocker)
    mock_user = mocker.MagicMock(spec=User)
    mock_chat = mocker.MagicMock(spec=Chat, tutor_id=1)

    mocks["chat_repo"].get_chat_by_id.return_value = mock_chat

    # Simulate the authorization service throwing a permission error
    mocks[
        "tutor_service"
    ].verify_user_can_access_tutor.side_effect = UserNotEnrolledError()

    with pytest.raises(UserNotEnrolledError):
        service.post_message(
            chat_id=5, query="Am I allowed here?", current_user=mock_user
        )

    mocks["rag_service"].answer_query.assert_not_called()
