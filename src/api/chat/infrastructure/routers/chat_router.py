from fastapi import APIRouter, Depends, Request, status

from src.api.auth.infrastructure.dependencies import get_current_user
from src.api.chat.infrastructure.dependencies import get_chat_service
from src.core.application.protocols import ChatServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import (
    ChatCreate,
    ChatResponse,
    ChatUpdate,
    MessageResponse,
    QueryRequest,
    QueryResponse,
)
from src.core.infrastructure.limiter import limiter

TAG = {
    "name": "Chat",
    "description": "Interface for managing chat sessions and conversations.",
}
router = APIRouter(prefix="/chats", tags=[TAG["name"]])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_new_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> ChatResponse:
    """
    Creates a new, private chat session for the current user with a specific tutor.
    """
    new_chat = chat_service.create_new_chat(
        tutor_id=chat_data.tutor_id, user=current_user, title=chat_data.title
    )
    return ChatResponse.model_validate(new_chat)


@router.get("", response_model=list[ChatResponse])
async def get_user_chats_for_tutor(
    tutor_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> list[ChatResponse]:
    """
    Retrieves all chats for the current user that are associated with a specific tutor.
    """
    chats = chat_service.get_chats_for_user_and_tutor(
        tutor_id=tutor_id, user=current_user
    )
    return [ChatResponse.model_validate(chat) for chat in chats]


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def get_chat_history(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> list[MessageResponse]:
    """Retrieves the full message history for a specific chat session."""
    history = chat_service.get_history(chat_id=chat_id, user=current_user)
    return [MessageResponse.model_validate(msg) for msg in history]


@router.post("/{chat_id}/query", response_model=QueryResponse)
@limiter.limit("20/minute")
async def post_message_to_chat(
    request: Request,
    chat_id: int,
    query_data: QueryRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> QueryResponse:
    """Posts a new message to a chat and gets a response from the AI Tutor."""
    answer = chat_service.post_message(
        chat_id=chat_id, query=query_data.query, current_user=current_user
    )
    return QueryResponse(answer=answer)


@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    chat_data: ChatUpdate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> ChatResponse:
    """Updates a chat session's details (e.g., renaming it)."""
    updated_chat = chat_service.update_chat(chat_id, chat_data, current_user)
    return ChatResponse.model_validate(updated_chat)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> None:
    """Deletes a chat session and all of its messages."""
    chat_service.delete_chat(chat_id, current_user)
