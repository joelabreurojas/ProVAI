from src.chat.application.exceptions import SessionNotFoundError
from src.chat.application.protocols import (
    SessionRepositoryProtocol,
    SessionServiceProtocol,
)
from src.chat.domain.models import Message, Session


class SessionService(SessionServiceProtocol):
    """
    It provides a simple interface for creating and logging interactions,
    as well as retrieving the history of interactions.
    """

    def __init__(self, session_repo: SessionRepositoryProtocol):
        self.session_repo = session_repo

    def get_or_create_session(self, chat_id: int, user_id: int) -> Session:
        latest_session = self.session_repo.get_latest_session(
            chat_id=chat_id, user_id=user_id
        )

        if latest_session:
            return latest_session

        return self.session_repo.create_session(chat_id=chat_id, user_id=user_id)

    def log_interaction(
        self, session_id: int, user_query: str, assistant_response: str
    ) -> None:
        self.session_repo.add_message(
            session_id=session_id, role="user", content=user_query
        )
        self.session_repo.add_message(
            session_id=session_id, role="assistant", content=assistant_response
        )

    def get_history(self, session_id: int) -> list[Message]:
        session = self.session_repo.get_session_by_id(session_id=session_id)
        if not session:
            raise SessionNotFoundError(session_id=session_id)

        return sorted(session.messages, key=lambda msg: msg.timestamp)
