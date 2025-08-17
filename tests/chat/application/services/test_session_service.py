from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from src.chat.application.protocols import SessionRepositoryProtocol
from src.chat.application.services import SessionService
from src.chat.domain.models import Session


def test_get_or_create_session_creates_new_session(mocker: MockerFixture) -> None:
    """Tests that a new session is created."""
    mock_session_repo = mocker.MagicMock(spec=SessionRepositoryProtocol)
    service = SessionService(session_repo=mock_session_repo)

    service.get_or_create_session(chat_id=1, user_id=101)

    mock_session_repo.create_session.assert_called_once_with(chat_id=1, user_id=101)


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

    # Create mock messages with out-of-order timestamps
    msg1 = MagicMock(timestamp="2025-01-01T12:00:00")
    msg3 = MagicMock(timestamp="2025-01-01T12:02:00")
    msg2 = MagicMock(timestamp="2025-01-01T12:01:00")

    mock_session = mocker.MagicMock(spec=Session)
    mock_session.messages = [msg1, msg3, msg2]  # Unordered

    mock_session_repo.get_session_by_id.return_value = mock_session
    service = SessionService(session_repo=mock_session_repo)

    result = service.get_history(session_id=5)

    mock_session_repo.get_session_by_id.assert_called_once_with(session_id=5)
    # Check that the returned list is now correctly ordered by the key lambda
    assert result == [msg1, msg2, msg3]
