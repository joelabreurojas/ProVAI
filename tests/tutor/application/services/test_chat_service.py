import pytest
from pytest_mock import MockerFixture

from src.tutor.application.exceptions import ChatNotFoundError
from src.tutor.application.protocols import ChatRepositoryProtocol
from src.tutor.application.services import ChatService
from src.tutor.domain.models import Chat


def test_create_new_chat_successfully(mocker: MockerFixture) -> None:
    """
    Tests that the service correctly calls the repository to create a new chat.
    """
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)
    service = ChatService(chat_repo=mock_chat_repo)

    tutor_id = 1
    user_id = 101
    title = "New Study Chat"

    service.create_new_chat(tutor_id=tutor_id, user_id=user_id, title=title)

    mock_chat_repo.create_chat.assert_called_once_with(
        tutor_id=tutor_id, user_id=user_id, title=title
    )


def test_get_chat_returns_chat_when_found(mocker: MockerFixture) -> None:
    """
    Tests that the service returns a chat object when the repository finds it.
    """
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)
    mock_chat = mocker.MagicMock(spec=Chat)
    mock_chat_repo.get_chat_by_id.return_value = mock_chat

    service = ChatService(chat_repo=mock_chat_repo)
    chat_id = 5

    result = service.get_chat(chat_id=chat_id)

    mock_chat_repo.get_chat_by_id.assert_called_once_with(chat_id=chat_id)
    assert result is mock_chat


def test_get_chat_raises_error_when_not_found(mocker: MockerFixture) -> None:
    """
    Tests that a ChatNotFoundError is raised if the repository
    does not find the chat.
    """
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)
    mock_chat_repo.get_chat_by_id.return_value = None  # Simulate not found

    service = ChatService(chat_repo=mock_chat_repo)
    chat_id = 999  # A chat that doesn't exist

    with pytest.raises(ChatNotFoundError):
        service.get_chat(chat_id=chat_id)

    mock_chat_repo.get_chat_by_id.assert_called_once_with(chat_id=chat_id)


def test_get_chats_for_user_calls_repository(mocker: MockerFixture) -> None:
    """
    Tests that the service correctly calls the repository to get all chats
    for a user within a specific tutor.
    """
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)
    service = ChatService(chat_repo=mock_chat_repo)
    tutor_id = 1
    user_id = 101

    service.get_chats(tutor_id=tutor_id, user_id=user_id)

    mock_chat_repo.get_chats_for_user.assert_called_once_with(user_id=user_id)


def test_log_interaction_adds_two_messages(mocker: MockerFixture) -> None:
    """
    Tests that log_interaction correctly adds two messages (one for the user,
    one for the tutor) to the repository.
    """
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)
    service = ChatService(chat_repo=mock_chat_repo)

    chat_id = 5
    user_query = "What is RAG?"
    tutor_response = "RAG stands for..."

    service.log_interaction(
        chat_id=chat_id,
        user_query=user_query,
        tutor_response=tutor_response,
    )

    assert mock_chat_repo.add_message.call_count == 2
    mock_chat_repo.add_message.assert_any_call(
        chat_id=chat_id, role="user", content=user_query
    )
    mock_chat_repo.add_message.assert_any_call(
        chat_id=chat_id, role="tutor", content=tutor_response
    )


def test_get_history_returns_sorted_messages(mocker: MockerFixture) -> None:
    """
    Tests that the get_history method correctly fetches a chat and returns
    its messages, sorted by timestamp.
    """
    mock_chat_repo = mocker.MagicMock(spec=ChatRepositoryProtocol)

    # Use mocker to create mock messages with out-of-order timestamps
    msg1 = mocker.MagicMock(timestamp="2025-01-01T12:00:00")
    msg3 = mocker.MagicMock(timestamp="2025-01-01T12:02:00")
    msg2 = mocker.MagicMock(timestamp="2025-01-01T12:01:00")

    mock_chat = mocker.MagicMock(spec=Chat)
    mock_chat.messages = [msg1, msg3, msg2]  # Unordered

    mock_chat_repo.get_chat_by_id.return_value = mock_chat
    service = ChatService(chat_repo=mock_chat_repo)

    result = service.get_history(chat_id=5)

    mock_chat_repo.get_chat_by_id.assert_called_once_with(chat_id=5)
    # Check that the returned list is now correctly ordered by the key lambda
    assert result == [msg1, msg2, msg3]
