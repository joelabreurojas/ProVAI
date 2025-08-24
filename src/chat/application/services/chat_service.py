from src.chat.application.exceptions import ChatNotFoundError
from src.chat.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
)
from src.chat.domain.models import Chat, Message


class ChatService(ChatServiceProtocol):
    """
    Orchestrates the business logic for managing Chats and Messages
    within a specific Tutor.
    """

    def __init__(self, chat_repo: ChatRepositoryProtocol):
        self.chat_repo = chat_repo

    def create_new_chat(self, tutor_id: int, user_id: int, title: str) -> Chat:
        return self.chat_repo.create_chat(
            tutor_id=tutor_id, user_id=user_id, title=title
        )

    def get_chat(self, chat_id: int) -> Chat:
        chat = self.chat_repo.get_chat_by_id(chat_id=chat_id)

        if not chat:
            raise ChatNotFoundError(chat_id=chat_id)
        return chat

    def get_chats(self, tutor_id: int, user_id: int) -> list[Chat]:
        """
        Gets all chats a specific user has participated in for a specific tutor.
        """
        all_user_chats = self.chat_repo.get_chats_for_user(user_id=user_id)

        tutor_chats = [chat for chat in all_user_chats if chat.tutor_id == tutor_id]

        return tutor_chats

    def log_interaction(
        self, chat_id: int, user_query: str, tutor_response: str
    ) -> None:
        self.chat_repo.add_message(chat_id=chat_id, role="user", content=user_query)
        self.chat_repo.add_message(
            chat_id=chat_id, role="tutor", content=tutor_response
        )

    def get_history(self, chat_id: int) -> list[Message]:
        chat = self.get_chat(chat_id=chat_id)
        return sorted(chat.messages, key=lambda msg: msg.timestamp)
