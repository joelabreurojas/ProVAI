from src.chat.application.protocols import (
    HistoryRepositoryProtocol,
    HistoryServiceProtocol,
)
from src.chat.domain.models import SessionHistory


class HistoryService(HistoryServiceProtocol):
    """
    The main application service for handling chat history business logic.
    """

    def __init__(self, history_repo: HistoryRepositoryProtocol):
        self.history_repo = history_repo

    def log_interaction(
        self, chat_id: int, user_id: int, query: str, response: str
    ) -> None:
        self.history_repo.add_interaction(
            chat_id=chat_id, user_id=user_id, query=query, response=response
        )

    def get_history(self, chat_id: int) -> list[SessionHistory]:
        return self.history_repo.get_history_by_chat_id(chat_id=chat_id)
