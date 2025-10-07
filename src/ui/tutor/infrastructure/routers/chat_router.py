# In src/ui/chat/infrastructure/routers/chat_router.py

import datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse

from src.core.application.protocols import ChatServiceProtocol, TutorServiceProtocol
from src.core.domain.models import Message, User
from src.core.domain.schemas import ChatUpdate, MessageUpdate
from src.ui.shared.infrastructure.dependencies import (
    get_authenticated_bff_api_client,
    get_current_user_from_cookie,
    get_sidebar_context,
    validate_csrf_token,
)
from src.ui.shared.infrastructure.utils import htmx_trigger, render_template
from src.ui.tutor.infrastructure.routers.tutor_router import get_chats_panel

router = APIRouter(prefix="/chats", tags=["UI - Chat"], include_in_schema=False)

# --- FULL PAGE ENDPOINTS ---


@router.get("/{chat_id}")
async def serve_chat_workspace(
    request: Request,
    chat_id: int,
    sidebar_context: dict[str, Any] = Depends(get_sidebar_context),
    chat_service: ChatServiceProtocol = Depends(),
    tutor_service: TutorServiceProtocol = Depends(),
    user: User = Depends(get_current_user_from_cookie),
) -> Response:
    """Serves the full-page chat workspace for a direct browser visit."""
    chat = chat_service.get_chat(chat_id, user)
    tutor = tutor_service.verify_user_can_access_tutor(chat.tutor_id, user)

    context = {
        "request": request,
        "title": f"Chat: {chat.title}",
        "active_tutor_id": tutor.id,
        "tutor": tutor,
        "chat": chat,
        "show_contextual_sidebar": True,
        "contextual_sidebar_url": f"/tutors/{tutor.id}/contextual-sidebar",
        **sidebar_context,
    }
    return render_template("tutor/chat_workspace.html", context)


# --- PARTIAL SWAP ENDPOINTS ---


@router.get("/{chat_id}/messaging-interface")
async def get_messaging_interface(
    request: Request,
    chat_id: int,
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Renders the HTML partial for the main messaging interface."""
    chat = chat_service.get_chat(chat_id, user)
    tutor = tutor_service.verify_user_can_access_tutor(chat.tutor_id, user)
    history = chat_service.get_history(chat_id, user)

    context = {
        "request": request,
        "user": user,
        "tutor": tutor,
        "chat": chat,
        "messages": history,
    }
    response = render_template("partials/tutor/_messaging_interface.html", context)
    return htmx_trigger(response, events={}, request=request)


@router.post("/{chat_id}/send-message")
async def handle_send_message(
    request: Request,
    chat_id: int,
    query: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    client: httpx.AsyncClient = Depends(get_authenticated_bff_api_client),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for sending a message and returning the user+AI response bubbles."""
    async with client as c:
        api_response = await c.post(f"/chats/{chat_id}/query", json={"query": query})
    api_response.raise_for_status()

    response_data = api_response.json()
    user_message = Message(**response_data["user_message"])
    ai_message = Message(**response_data["ai_message"])

    user_bubble_html = render_template(
        "partials/tutor/_message_bubble.html",
        {"request": request, "user": user, "message": user_message},
    ).body.decode()
    ai_bubble_html = render_template(
        "partials/tutor/_message_bubble.html",
        {"request": request, "user": user, "message": ai_message},
    ).body.decode()

    response = Response(content=user_bubble_html + ai_bubble_html)
    return htmx_trigger(response, events={}, request=request)


@router.post("/{chat_id}/delete")
async def handle_delete_chat_from_workspace(
    request: Request,
    chat_id: int,
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
    client: httpx.AsyncClient = Depends(get_authenticated_bff_api_client),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """Handles deleting a chat from its own workspace and forces a full redirect."""
    chat = chat_service.get_chat(chat_id, user)
    tutor_id = chat.tutor_id

    async with client as c:
        await c.delete(f"/chats/{chat.id}")

    request.session["toast_message"] = "Chat deleted successfully."
    request.session["toast_category"] = "success"

    response = Response()
    response.headers["HX-Redirect"] = f"/tutors/{tutor_id}"
    return response


# --- INLINE EDIT/DELETE (CHAT LIST) ---


@router.post("/{chat_id}/edit")
async def handle_update_chat_title(
    request: Request,
    chat_id: int,
    title: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
    tutor_service: TutorServiceProtocol = Depends(),
    client: httpx.AsyncClient = Depends(get_authenticated_bff_api_client),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """Handles renaming a chat from the list view and returns the refreshed panel."""
    chat = chat_service.get_chat(chat_id, user)
    tutor_id = chat.tutor_id
    chat_update = ChatUpdate(title=title)

    async with client as c:
        await c.patch(f"/chats/{chat_id}", json=chat_update.model_dump())

    return await get_chats_panel(request, tutor_id, user, chat_service, tutor_service)


@router.post("/{chat_id}/delete-inline")
async def handle_delete_chat_inline(
    request: Request,
    chat_id: int,
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
    tutor_service: TutorServiceProtocol = Depends(),
    client: httpx.AsyncClient = Depends(get_authenticated_bff_api_client),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """Handles deleting a chat from the list view and returns the refreshed panel."""
    chat = chat_service.get_chat(chat_id, user)
    tutor_id = chat.tutor_id

    async with client as c:
        await c.delete(f"/chats/{chat.id}")

    return await get_chats_panel(request, tutor_id, user, chat_service, tutor_service)


# --- INLINE EDIT/DELETE (MESSAGE BUBBLE) ---


@router.get("/{message_id}/edit-form")
async def get_message_edit_form(
    request: Request,
    message_id: int,
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
) -> Response:
    """Renders the inline edit form for a single message."""
    message = chat_service.get_message_by_id_for_user(message_id, user)
    context = {"request": request, "user": user, "message": message}

    # Render the template first
    response = render_template("partials/tutor/_edit_message_form.html", context)

    # THE FIX: Wrap the response to refresh the token on form load.
    return htmx_trigger(response, events={}, request=request)


@router.post("/{message_id}/edit-message")
async def handle_edit_user_message(
    request: Request,
    message_id: int,
    content: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
    client: httpx.AsyncClient = Depends(get_authenticated_bff_api_client),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """Edits a user message and returns the re-rendered message bubble."""
    message_update = MessageUpdate(content=content)

    async with client as c:
        api_response = await c.patch(
            f"/messages/{message_id}", json=message_update.model_dump()
        )
    api_response.raise_for_status()

    updated_message = Message(**api_response.json())

    context = {"request": request, "user": user, "message": updated_message}
    response = render_template("partials/tutor/_message_bubble.html", context)
    return htmx_trigger(response, events={}, request=request)


@router.get("/{message_id}/message-bubble")
async def get_message_bubble(
    request: Request,
    message_id: int,
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
) -> Response:
    """Renders a single message bubble (used for cancel)."""
    message = chat_service.get_message_by_id_for_user(message_id, user)
    context = {"request": request, "user": user, "message": message}
    return render_template("partials/tutor/_message_bubble.html", context)


@router.post("/{message_id}/delete-message")
async def handle_delete_message(
    request: Request,
    message_id: int,
    client: httpx.AsyncClient = Depends(get_authenticated_bff_api_client),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for deleting a single message."""
    async with client as c:
        await c.delete(f"/messages/{message_id}")
    return Response(status_code=status.HTTP_200_OK)


@router.post("/{message_id}/regenerate-message")
async def handle_regenerate_ai_message(
    request: Request,
    message_id: int,
    user: User = Depends(get_current_user_from_cookie),
    client: httpx.AsyncClient = Depends(get_authenticated_bff_api_client),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for regenerating an AI message."""
    async with client as c:
        api_response = await c.post(f"/messages/{message_id}/regenerate")
    api_response.raise_for_status()

    updated_ai_message = Message(**api_response.json())
    context = {"request": request, "user": user, "message": updated_ai_message}
    response = render_template("partials/tutor/_message_bubble.html", context)
    return htmx_trigger(response, events={}, request=request)
