from sqlalchemy import desc
from sqlalchemy.orm import Session as SQLAlchemySession

from src.assistant.application.protocols import ChatRepositoryProtocol
from src.assistant.domain.models import Chat, Message


class SQLAlchemyChatRepository(ChatRepositoryProtocol):
    """
    Concrete implementation of the Chat and Message repository using SQLAlchemy.
    """

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def create_chat(self, assistant_id: int, user_id: int, title: str) -> Chat:
        db_chat = Chat(assistant_id=assistant_id, user_id=user_id, title=title)
        self.db.add(db_chat)
        self.db.commit()
        self.db.refresh(db_chat)
        return db_chat

    def get_chat_by_id(self, chat_id: int) -> Chat | None:
        return self.db.query(Chat).filter(Chat.id == chat_id).first()

    def get_chats_for_user(self, user_id: int) -> list[Chat]:
        return (
            self.db.query(Chat)
            .filter_by(user_id=user_id)
            .order_by(desc(Chat.created_at))
            .all()
        )

    def add_message(self, chat_id: int, role: str, content: str) -> Message:
        db_message = Message(chat_id=chat_id, role=role, content=content)
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
