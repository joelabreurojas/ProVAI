from src.assistant.application.exceptions import ChatNotFoundError
from src.assistant.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
)
from src.assistant.domain.models import Chat, Message


class ChatService(ChatServiceProtocol):
    def __init__(self, chat_repo: ChatRepositoryProtocol):
        self.chat_repo = chat_repo

    def create_new_chat(self, assistant_id: int, user_id: int, title: str) -> Chat:
        return self.chat_repo.create_chat(
            assistant_id=assistant_id, user_id=user_id, title=title
        )

    def get_chat(self, chat_id: int) -> Chat:
        chat = self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise ChatNotFoundError(chat_id=chat_id)
        return chat

    def get_chats(self, assistant_id: int, user_id: int) -> list[Chat]:
        return self.chat_repo.get_chats(assistant_id, user_id)

    def log_interaction(
        self, chat_id: int, user_query: str, assistant_response: str
    ) -> None:
        self.chat_repo.add_message(chat_id=chat_id, role="user", content=user_query)
        self.chat_repo.add_message(
            chat_id=chat_id, role="assistant", content=assistant_response
        )

    def get_history(self, chat_id: int) -> list[Message]:
        chat = self.get_chat(chat_id)
        return sorted(chat.messages, key=lambda msg: msg.timestamp)
