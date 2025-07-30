from sqlalchemy import asc
from sqlalchemy.orm import Session

from src.chat.application.protocols import HistoryRepositoryProtocol
from src.chat.domain.models import SessionHistory


class SQLAlchemyHistoryRepository(HistoryRepositoryProtocol):
    """Concrete implementation of the history repository using SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def add_interaction(
        self, chat_id: int, user_id: int, query: str, response: str
    ) -> SessionHistory:
        db_interaction = SessionHistory(
            chat_id=chat_id, user_id=user_id, query=query, response=response
        )
        self.db.add(db_interaction)
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def get_history_by_chat_id(self, chat_id: int) -> list[SessionHistory]:
        return (
            self.db.query(SessionHistory)
            .filter(SessionHistory.chat_id == chat_id)
            .order_by(asc(SessionHistory.timestamp))
            .all()
        )
