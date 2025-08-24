from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.auth.domain.models import User
from src.chat.application.protocols import ChatServiceProtocol
from src.chat.dependencies import get_chat_service
from src.chat.domain.schemas import (
    ChatCreate,
    ChatResponse,
    MessageResponse,
    QueryRequest,
    QueryResponse,
)

TAG = {
    "name": "Chat",
    "description": "The primary interface for all user-tutor conversations.",
}
router = APIRouter(prefix="/chats", tags=[TAG["name"]])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_new_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> ChatResponse:
    new_chat = chat_service.create_new_chat(
        tutor_id=chat_data.tutor_id, user=current_user, title=chat_data.title
    )
    return ChatResponse.model_validate(new_chat)


@router.post("/{chat_id}/query", response_model=QueryResponse)
async def post_message_to_chat(
    chat_id: int,
    query_data: QueryRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> QueryResponse:
    answer = chat_service.post_message(
        chat_id=chat_id, query=query_data.query, current_user=current_user
    )
    return QueryResponse(answer=answer)


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def get_chat_history(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> list[MessageResponse]:
    history = chat_service.get_history(chat_id=chat_id, user=current_user)
    return [MessageResponse.model_validate(msg) for msg in history]
