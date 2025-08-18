from pytest_mock import MockerFixture

from src.chat.application.protocols import SessionRepositoryProtocol
from src.chat.application.services import SessionService
from src.chat.domain.models import Session


def test_get_or_create_session_returns_existing_session(mocker: MockerFixture) -> None:
    """
    Tests that if a recent session exists, it is returned and a new
    one is NOT created.
    """
    mock_session_repo = mocker.MagicMock(spec=SessionRepositoryProtocol)
    mock_existing_session = mocker.MagicMock(spec=Session)

    mock_session_repo.get_latest_session.return_value = mock_existing_session

    service = SessionService(session_repo=mock_session_repo)

    result = service.get_or_create_session(chat_id=1, user_id=101)

    # It should have tried to find a session.
    mock_session_repo.get_latest_session.assert_called_once_with(chat_id=1, user_id=101)
    # It should NOT have created a new one.
    mock_session_repo.create_session.assert_not_called()
    # It should have returned the session it found.
    assert result is mock_existing_session


def test_get_or_create_session_creates_new_session_if_none_exist(
    mocker: MockerFixture,
) -> None:
    """
    Tests that if no recent session exists, a new one is created and returned.
    """
    mock_session_repo = mocker.MagicMock(spec=SessionRepositoryProtocol)
    mock_new_session = mocker.MagicMock(spec=Session)

    # Configure the mock to simulate NOT finding an existing session.
    mock_session_repo.get_latest_session.return_value = None
    # Configure the mock for what happens when a new session is created.
    mock_session_repo.create_session.return_value = mock_new_session

    service = SessionService(session_repo=mock_session_repo)

    result = service.get_or_create_session(chat_id=1, user_id=101)

    # It should have tried to find a session.
    mock_session_repo.get_latest_session.assert_called_once_with(chat_id=1, user_id=101)
    # Because it found none, it SHOULD have created a new one.
    mock_session_repo.create_session.assert_called_once_with(chat_id=1, user_id=101)
    # It should have returned the newly created session.
    assert result is mock_new_session


def test_log_interaction_adds_two_messages(mocker: MockerFixture) -> None:
    """
    Tests that log_interaction correctly adds two messages (one for the user,
    one for the assistant) to the repository.
    """
    mock_session_repo = mocker.MagicMock(spec=SessionRepositoryProtocol)
    service = SessionService(session_repo=mock_session_repo)

    session_id = 5
    user_query = "What is RAG?"
    assistant_response = "RAG stands for..."

    service.log_interaction(
        session_id=session_id,
        user_query=user_query,
        assistant_response=assistant_response,
    )

    assert mock_session_repo.add_message.call_count == 2
    mock_session_repo.add_message.assert_any_call(
        session_id=session_id, role="user", content=user_query
    )
    mock_session_repo.add_message.assert_any_call(
        session_id=session_id, role="assistant", content=assistant_response
    )


def test_get_history_returns_sorted_messages(mocker: MockerFixture) -> None:
    """
    Tests that the get_history method correctly fetches a session and returns
    its messages, sorted by timestamp.
    """
    mock_session_repo = mocker.MagicMock(spec=SessionRepositoryProtocol)

    # Out-of-order timestamps
    msg1 = mocker.MagicMock(timestamp="2025-01-01T12:00:00")
    msg3 = mocker.MagicMock(timestamp="2025-01-01T12:02:00")
    msg2 = mocker.MagicMock(timestamp="2025-01-01T12:01:00")

    mock_session = mocker.MagicMock(spec=Session)
    mock_session.messages = [msg1, msg3, msg2]  # Unordered

    mock_session_repo.get_session_by_id.return_value = mock_session
    service = SessionService(session_repo=mock_session_repo)

    result = service.get_history(session_id=5)

    mock_session_repo.get_session_by_id.assert_called_once_with(session_id=5)
    # Check that the returned list is now correctly ordered by the key lambda
    assert result == [msg1, msg2, msg3]
