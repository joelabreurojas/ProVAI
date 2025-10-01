import logging

from langsmith import traceable

from src.core.application.exceptions import (
    AIMessageEditError,
    ChatNotFoundError,
    ChatOwnershipError,
    MessageNotFoundError,
)
from src.core.application.protocols import (
    ChatRepositoryProtocol,
    ChatServiceProtocol,
    IngestionServiceProtocol,
    RAGServiceProtocol,
    TutorRepositoryProtocol,
    TutorServiceProtocol,
)
from src.core.domain.models import Chat, Document, Message, User
from src.core.domain.schemas import ChatUpdate, MessageUpdate

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

    def _authorize_chat_owner(self, chat: Chat, user: User) -> None:
        """
        A private helper to verify that the user is the owner of the chat.
        This is a more specific check than just being enrolled in the tutor.
        """
        self.tutor_service.verify_user_can_access_tutor(chat.tutor_id, user)

        if chat.user_id != user.id:
            raise ChatOwnershipError()

    @traceable(name="Create Chat")
    def create_new_chat(self, tutor_id: int, user: User, title: str) -> Chat:
        self.tutor_service.verify_user_can_access_tutor(tutor_id, user)
        return self.chat_repo.create_chat(
            tutor_id=tutor_id, user_id=user.id, title=title
        )

    def get_chat(self, chat_id: int, user: User) -> Chat:
        chat = self.chat_repo.get_chat_by_id(chat_id=chat_id)
        if not chat:
            raise ChatNotFoundError(chat_id=chat_id)
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
        chat = self.get_chat(chat_id, user)
        self._authorize_chat_owner(chat, user)
        return sorted(chat.messages, key=lambda msg: msg.timestamp)

    @traceable(name="Add Document")
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

    def update_chat(
        self, chat_id: int, chat_update: ChatUpdate, requesting_user: User
    ) -> Chat:
        chat = self.get_chat(chat_id, requesting_user)
        self._authorize_chat_owner(chat, requesting_user)
        return self.chat_repo.update_chat(chat, chat_update)

    def delete_chat(self, chat_id: int, requesting_user: User) -> None:
        chat = self.get_chat(chat_id, requesting_user)
        self._authorize_chat_owner(chat, requesting_user)
        self.chat_repo.delete_chat(chat)

    @traceable(name="Post Message")
    def post_message(self, chat_id: int, query: str, current_user: User) -> str:
        """Orchestrates the full query -> RAG -> response -> log workflow."""
        chat = self.get_chat(chat_id, current_user)
        self._authorize_chat_owner(chat, current_user)
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

    @traceable(name="Regenerate Response")
    def regenerate_response(self, message_id: int, requesting_user: User) -> Message:
        """
        Finds an AI Tutor message, re-runs the RAG pipeline using the
        preceding user query, and updates the AI message with the new response.
        """
        ai_message = self.chat_repo.get_message_by_id(message_id)
        if not ai_message:
            raise MessageNotFoundError()

        # Authorize the user owns the chat
        self._authorize_chat_owner(ai_message.chat, requesting_user)

        # Verify we are regenerating an AI message
        if ai_message.role != "tutor":
            raise AIMessageEditError("Can only regenerate responses from the AI tutor.")

        # Find the original user query
        original_user_message = self.chat_repo.get_preceding_user_message(ai_message)
        if not original_user_message:
            raise AIMessageEditError(
                "Could not find a preceding user query to regenerate."
            )

        # Re-run the RAG pipeline directly
        valid_chunk_hashes = self.tutor_repo.get_chunk_hashes_for_tutor(
            ai_message.chat.tutor_id
        )
        if not valid_chunk_hashes:
            # This case is unlikely but handled for robustness
            new_answer = "This tutor no longer has documents to reference."
        else:
            context_filter = {"content_hash": {"$in": valid_chunk_hashes}}
            new_answer = self.rag_service.answer_query(
                original_user_message.content, context_filter
            )

        # Update the existing message in the database with the new content
        return self.chat_repo.update_message(
            ai_message, MessageUpdate(content=new_answer)
        )

    def update_user_message(
        self, message_id: int, message_update: MessageUpdate, requesting_user: User
    ) -> Message:
        message = self.chat_repo.get_message_by_id(message_id)
        if not message:
            raise MessageNotFoundError()

        self._authorize_chat_owner(message.chat, requesting_user)

        if message.role != "user":
            raise AIMessageEditError()

        return self.chat_repo.update_message(message, message_update)

    def delete_message(self, message_id: int, requesting_user: User) -> None:
        message = self.chat_repo.get_message_by_id(message_id)
        if not message:
            raise MessageNotFoundError()

        self._authorize_chat_owner(message.chat, requesting_user)
        self.chat_repo.delete_message(message)
