from sqlalchemy import desc
from sqlalchemy.orm import Session as SQLAlchemySession

from src.core.application.protocols import ChatRepositoryProtocol
from src.core.domain.models import Chat, Message
from src.core.domain.schemas import ChatUpdate, MessageUpdate


class SQLAlchemyChatRepository(ChatRepositoryProtocol):
    """
    Concrete implementation of the Chat and Message repository using SQLAlchemy.
    """

    def __init__(self, db: SQLAlchemySession) -> None:
        self.db = db

    def create_chat(self, tutor_id: int, user_id: int, title: str) -> Chat:
        db_chat = Chat(tutor_id=tutor_id, user_id=user_id, title=title)
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

    def update_chat(self, chat: Chat, chat_update: ChatUpdate) -> Chat:
        chat.title = chat_update.title
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def delete_chat(self, chat: Chat) -> None:
        self.db.delete(chat)
        self.db.commit()

    def add_message(self, chat_id: int, role: str, content: str) -> Message:
        db_message = Message(chat_id=chat_id, role=role, content=content)
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_message_by_id(self, message_id: int) -> Message | None:
        return self.db.get(Message, message_id)

    def get_preceding_user_message(self, ai_message: Message) -> Message | None:
        """
        Finds the most recent user message in the same chat that occurred
        before the given AI message.
        """
        return (
            self.db.query(Message)
            .filter(
                Message.chat_id == ai_message.chat_id,
                Message.role == "user",
                Message.timestamp < ai_message.timestamp,
            )
            .order_by(Message.timestamp.desc())
            .first()
        )

    def update_message(
        self, message: Message, message_update: MessageUpdate
    ) -> Message:
        message.content = message_update.content
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def delete_message(self, message: Message) -> None:
        self.db.delete(message)
        self.db.commit()
