from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.chat.infrastructure.repositories import SQLAlchemyChatRepository
from src.core.infrastructure.settings import settings
from tests.helpers import STUDENT_A_EMAIL, setup_users_and_tutor


def test_user_can_rename_and_delete_their_own_chat(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests the full lifecycle of a chat: create, update (rename), and delete.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]
    student_headers = context["student_a_headers"]
    teacher_headers = context["teacher_headers"]

    # Enroll the student
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}", headers=teacher_headers
    )
    invitation_token = tutor_details_res.json()["token"]
    client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/authorized-emails",
        json={"emails": [STUDENT_A_EMAIL]},
        headers=teacher_headers,
    )
    enrollment_res = client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=student_headers,
    )
    assert enrollment_res.status_code == 201

    # Create a chat
    create_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Initial Chat Name"},
        headers=student_headers,
    )
    assert create_res.status_code == 201
    chat_id = create_res.json()["id"]
    assert create_res.json()["title"] == "Initial Chat Name"

    # Update (rename) the chat
    update_res = client.patch(
        f"{settings.API_ROOT_PATH}/chats/{chat_id}",
        json={"title": "Updated Chat Name"},
        headers=student_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Chat Name"

    # Another user (the teacher) CANNOT update the chat
    unauthorized_update_res = client.patch(
        f"{settings.API_ROOT_PATH}/chats/{chat_id}",
        json={"title": "Unauthorized Update"},
        headers=context["teacher_headers"],  # Using the wrong user
    )
    assert unauthorized_update_res.status_code == 403
    assert unauthorized_update_res.json()["error_code"] == "CHAT_OWNERSHIP_REQUIRED"

    # Delete the chat
    delete_res = client.delete(
        f"{settings.API_ROOT_PATH}/chats/{chat_id}", headers=student_headers
    )
    assert delete_res.status_code == 204

    # Verify the chat is gone
    get_res = client.get(
        f"{settings.API_ROOT_PATH}/chats/{chat_id}/messages", headers=student_headers
    )
    assert get_res.status_code == 404  # Chat not found


def test_user_can_edit_and_delete_messages(
    client: TestClient, db_session: SQLAlchemySession
) -> None:
    """
    Tests that a user can edit/delete their own messages and delete AI messages,
    without invoking the actual RAG pipeline.
    """
    context = setup_users_and_tutor(client, db_session)
    tutor_id = context["tutor_id"]
    student_headers = context["student_a_headers"]
    teacher_headers = context["teacher_headers"]

    # Enroll the student
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}", headers=teacher_headers
    )
    invitation_token = tutor_details_res.json()["token"]
    client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/authorized-emails",
        json={"emails": [STUDENT_A_EMAIL]},
        headers=teacher_headers,
    )
    enrollment_res = client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=student_headers,
    )
    assert enrollment_res.status_code == 201

    # Create a chat
    chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "Message Test Chat"},
        headers=student_headers,
    )
    chat_id = chat_res.json()["id"]

    # Directly create the messages using the repository for a clean state
    chat_repo = SQLAlchemyChatRepository(db_session)
    user_message = chat_repo.add_message(chat_id, "user", "Original user message")
    ai_message = chat_repo.add_message(chat_id, "tutor", "Original AI response")

    user_message_id = user_message.id
    ai_message_id = ai_message.id

    # User successfully EDITS their own message
    edit_res = client.patch(
        f"{settings.API_ROOT_PATH}/messages/{user_message_id}",
        json={"content": "Edited user message"},
        headers=student_headers,
    )
    assert edit_res.status_code == 200
    assert edit_res.json()["content"] == "Edited user message"

    # User CANNOT edit the AI's message
    unauthorized_edit_res = client.patch(
        f"{settings.API_ROOT_PATH}/messages/{ai_message_id}",
        json={"content": "Attempted edit of AI message"},
        headers=student_headers,
    )
    assert unauthorized_edit_res.status_code == 403
    assert unauthorized_edit_res.json()["error_code"] == "AI_MESSAGE_EDIT_NOT_ALLOWED"

    # User successfully DELETES the AI's message
    delete_ai_res = client.delete(
        f"{settings.API_ROOT_PATH}/messages/{ai_message_id}",
        headers=student_headers,
    )
    assert delete_ai_res.status_code == 204

    # User successfully DELETES their own message
    delete_user_res = client.delete(
        f"{settings.API_ROOT_PATH}/messages/{user_message_id}",
        headers=student_headers,
    )
    assert delete_user_res.status_code == 204

    # Verify history is now empty
    final_history_res = client.get(
        f"{settings.API_ROOT_PATH}/chats/{chat_id}/messages", headers=student_headers
    )
    assert len(final_history_res.json()) == 0
