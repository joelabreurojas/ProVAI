from pytest_mock import MockerFixture

from src.chat.application.protocols import HistoryRepositoryProtocol
from src.chat.application.services import HistoryService


def test_log_interaction_calls_repository_correctly(mocker: MockerFixture) -> None:
    """
    Tests that the HistoryService's log_interaction method correctly calls
    the underlying repository with the provided data.
    """
    mock_history_repo = mocker.MagicMock(spec=HistoryRepositoryProtocol)
    history_service = HistoryService(history_repo=mock_history_repo)

    chat_id = 1
    user_id = 101
    query = "What is the RAG pipeline?"
    response = "It is a way to augment LLMs with external knowledge."

    history_service.log_interaction(
        chat_id=chat_id, user_id=user_id, query=query, response=response
    )

    mock_history_repo.add_interaction.assert_called_once_with(
        chat_id=chat_id, user_id=user_id, query=query, response=response
    )


def test_get_history_calls_repository_and_returns_data(mocker: MockerFixture) -> None:
    """
    Tests that the HistoryService's get_history method correctly calls
    the repository and returns its result.
    """
    mock_history_repo = mocker.MagicMock(spec=HistoryRepositoryProtocol)
    expected_history = [mocker.MagicMock(), mocker.MagicMock()]
    mock_history_repo.get_history_by_chat_id.return_value = expected_history

    history_service = HistoryService(history_repo=mock_history_repo)
    chat_id = 1

    result = history_service.get_history(chat_id=chat_id)

    mock_history_repo.get_history_by_chat_id.assert_called_once_with(chat_id=chat_id)
    assert result == expected_history
