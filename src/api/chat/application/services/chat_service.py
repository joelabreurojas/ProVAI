import logging

from langsmith import traceable

from src.core.application.exceptions import ChatNotFoundError
from src.core.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
    IngestionServiceProtocol,
    RAGServiceProtocol,
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.core.domain.models import Chat, Document, Message, User

logger = logging.getLogger(__name__)


class ChatService(ChatServiceProtocol):
    def __init__(
        self,
        chat_repo: ChatRepositoryProtocol,
        tutor_service: TutorServiceProtocol,
        rag_service: RAGServiceProtocol,
        ingestion_service: IngestionServiceProtocol,
        tutor_repo: TutorRepositoryProtocol,
    ):
        self.chat_repo = chat_repo
        self.tutor_service = tutor_service
        self.rag_service = rag_service
        self.ingestion_service = ingestion_service
        self.tutor_repo = tutor_repo

    @traceable(name="Create Chat")
    def create_new_chat(self, tutor_id: int, user: User, title: str) -> Chat:
        self.tutor_service.verify_user_can_access_tutor(tutor_id, user)
        return self.chat_repo.create_chat(
            tutor_id=tutor_id, user_id=user.id, title=title
        )

    @traceable(name="Add Document")
    def get_chat(self, chat_id: int, user: User) -> Chat:
        chat = self.chat_repo.get_chat_by_id(chat_id=chat_id)
        if not chat:
            raise ChatNotFoundError(chat_id=chat_id)
        self.tutor_service.verify_user_can_access_tutor(chat.tutor_id, user)
        return chat

    def get_chats_for_user_and_tutor(self, tutor_id: int, user: User) -> list[Chat]:
        """
        Gets all chats a specific user has participated in for a specific tutor.
        First, it authorizes that the user has access to the parent tutor.
        """
        self.tutor_service.verify_user_can_access_tutor(tutor_id, user)
        all_user_chats = self.chat_repo.get_chats_for_user(user_id=user.id)
        tutor_specific_chats = [
            chat for chat in all_user_chats if chat.tutor_id == tutor_id
        ]
        return tutor_specific_chats

    def get_history(self, chat_id: int, user: User) -> list[Message]:
        chat = self.get_chat(chat_id, user)  # Authorization happens here
        return sorted(chat.messages, key=lambda msg: msg.timestamp)

    def add_document_to_chat(
        self, chat_id: int, file_bytes: bytes, file_name: str, current_user: User
    ) -> Document:
        """Orchestrates adding a document to a chat's parent tutor."""
        chat = self.get_chat(chat_id, current_user)
        tutor = self.tutor_service.get_tutor(chat.tutor_id)
        self.tutor_service.verify_user_is_tutor_owner(tutor.id, current_user)
        new_document = self.ingestion_service.ingest_document(file_bytes, file_name)
        self.tutor_repo.link_document_to_tutor(tutor, new_document)
        return new_document

    @traceable(name="Post Message")
    def post_message(self, chat_id: int, query: str, current_user: User) -> str:
        """Orchestrates the full query -> RAG -> response -> log workflow."""
        chat = self.get_chat(chat_id, current_user)
        self.log_interaction(chat_id, user_query=query, role="user")

        valid_chunk_hashes = self.tutor_repo.get_chunk_hashes_for_tutor(chat.tutor_id)
        if not valid_chunk_hashes:
            answer = """This tutor has no documents yet.
            The teacher have to upload a document."""
            self.log_interaction(chat_id, tutor_response=answer, role="tutor")
            return answer

        context_filter = {"content_hash": {"$in": valid_chunk_hashes}}
        answer = self.rag_service.answer_query(query, context_filter)
        self.log_interaction(chat_id, tutor_response=answer, role="tutor")
        return answer

    def log_interaction(
        self,
        chat_id: int,
        role: str,
        user_query: str | None = None,
        tutor_response: str | None = None,
    ) -> None:
        if role == "user" and user_query:
            self.chat_repo.add_message(chat_id=chat_id, role="user", content=user_query)
        elif role == "tutor" and tutor_response:
            self.chat_repo.add_message(
                chat_id=chat_id, role="tutor", content=tutor_response
            )
