from sqlalchemy import desc
from sqlalchemy.orm import Session as SQLAlchemySession

from src.chat.application.protocols import SessionRepositoryProtocol
from src.chat.domain.models import Message, Session


class SQLAlchemySessionRepository(SessionRepositoryProtocol):
    """Concrete implementation of the Session repository using SQLAlchemy."""

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def create_session(self, chat_id: int, user_id: int) -> Session:
        db_session = Session(chat_id=chat_id, user_id=user_id)
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def get_session_by_id(self, session_id: int) -> Session | None:
        return self.db.query(Session).filter(Session.id == session_id).first()

    def get_latest_session(self, chat_id: int, user_id: int) -> Session | None:
        return (
            self.db.query(Session)
            .filter_by(chat_id=chat_id, user_id=user_id)
            .order_by(desc(Session.created_at))
            .first()
        )

    def add_message(self, session_id: int, role: str, content: str) -> Message:
        db_message = Message(session_id=session_id, role=role, content=content)
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
