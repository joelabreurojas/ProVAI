from src.chat.application.protocols import (
    HistoryRepositoryProtocol,
    HistoryServiceProtocol,
)
from src.chat.domain.models import Message, Session


class HistoryService(HistoryServiceProtocol):
    def __init__(self, history_repo: HistoryRepositoryProtocol):
        self.history_repo = history_repo

    def get_or_create_session(self, chat_id: int, user_id: int) -> Session:
        # This is a placeholder for real logic. In a real app, we
        # first try to find an active session before creating a new one.
        return self.history_repo.create_session(chat_id=chat_id, user_id=user_id)

    def log_interaction(
        self, session_id: int, user_query: str, assistant_response: str
    ) -> None:
        self.history_repo.add_message(
            session_id=session_id, role="user", content=user_query
        )
        self.history_repo.add_message(
            session_id=session_id, role="assistant", content=assistant_response
        )

    def get_history(self, session_id: int) -> list[Message]:
        session = self.history_repo.get_session_by_id(session_id=session_id)
        if session:
            return sorted(session.messages, key=lambda msg: msg.timestamp)
        return []
