from fastapi import APIRouter, Depends, status

from src.api.auth.infrastructure.dependencies import get_current_user
from src.api.chat.infrastructure.dependencies import get_chat_service
from src.core.application.protocols import ChatServiceProtocol
from src.core.domain.models import User
from src.core.domain.schemas import MessageResponse, MessageUpdate

TAG = {"name": "Messages", "description": "Manage individual chat messages."}
router = APIRouter(prefix="/messages", tags=[TAG["name"]])


@router.patch("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    message_data: MessageUpdate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> MessageResponse:
    """Updates the content of a user's message."""
    updated_message = chat_service.update_user_message(
        message_id, message_data, current_user
    )
    return MessageResponse.model_validate(updated_message)


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> None:
    """Deletes a message from a chat."""
    chat_service.delete_message(message_id, current_user)


@router.post("/{message_id}/regenerate", response_model=MessageResponse)
async def regenerate_ai_response(
    message_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatServiceProtocol = Depends(get_chat_service),
) -> MessageResponse:
    """Regenerates the content of an AI Tutor's message."""
    regenerated_message = chat_service.regenerate_response(message_id, current_user)
    return MessageResponse.model_validate(regenerated_message)
