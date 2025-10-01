import fitz
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session as SQLAlchemySession

from src.api.ai.infrastructure.dependencies import get_llm_service
from src.api.rag.infrastructure.dependencies import get_rag_vector_store
from src.core.domain.models import User
from src.core.infrastructure.settings import settings

VALID_TEACHER_PASSWORD = "TeacherPassword123!"
VALID_STUDENT_PASSWORD = "StudentPassword456!"


def test_full_user_flow(
    app: FastAPI,
    client: TestClient,
    db_session: SQLAlchemySession,
    mocker: MockerFixture,
) -> None:
    """
    Tests the definitive, decoupled, end-to-end workflow.

    The Story:
    1. A Teacher and a Student are registered and log in.
    2. The Teacher creates a Tutor.
    3. The Teacher UPLOADS A DOCUMENT directly to the Tutor's knowledge base.
    4. The Teacher invites the Student to the Tutor.
    5. The Student enrolls.
    6. The Student CREATES THEIR OWN PRIVATE CHAT with the Tutor.
    7. The Student asks a question in their chat and gets a correct,
       context-aware answer.
    """

    # Register users & manually promote Teacher
    client.post(
        f"{settings.API_ROOT_PATH}/auth/register",
        json={
            "name": "E2E Teacher",
            "email": "teacher@e2e.com",
            "password": VALID_TEACHER_PASSWORD,
        },
    )
    teacher_db = db_session.query(User).filter_by(email="teacher@e2e.com").first()
    assert teacher_db is not None
    teacher_db.role = "teacher"
    db_session.commit()
    db_session.refresh(teacher_db)

    client.post(
        f"{settings.API_ROOT_PATH}/auth/register",
        json={
            "name": "E2E Student",
            "email": "student@e2e.com",
            "password": VALID_STUDENT_PASSWORD,
        },
    )

    # Both users log in
    teacher_login_res = client.post(
        f"{settings.API_ROOT_PATH}/auth/token",
        data={"email": "teacher@e2e.com", "password": VALID_TEACHER_PASSWORD},
    )
    teacher_token = teacher_login_res.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    student_login_res = client.post(
        f"{settings.API_ROOT_PATH}/auth/token",
        data={"email": "student@e2e.com", "password": VALID_STUDENT_PASSWORD},
    )
    student_token = student_login_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Teacher creates a Tutor
    tutor_res = client.post(
        f"{settings.API_ROOT_PATH}/tutors",
        json={"course_name": "E2E Test Course"},
        headers=teacher_headers,
    )
    assert tutor_res.status_code == 201
    tutor_id = tutor_res.json()["id"]

    # Teacher uploads a document to the Tutor
    mock_vector_store = mocker.MagicMock()
    mock_llm = mocker.MagicMock()
    app.dependency_overrides[get_rag_vector_store] = lambda: mock_vector_store
    app.dependency_overrides[get_llm_service] = lambda: mock_llm

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "This is a test PDF about multi-head attention.")
    pdf_bytes = doc.write()
    doc.close()

    upload_res = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/documents",
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
        headers=teacher_headers,
    )
    assert upload_res.status_code == 201, f"Document upload failed: {upload_res.json()}"

    # Teacher adds student's email to the whitelist.
    add_email_res = client.post(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}/authorized-emails",
        json={"emails": ["student@e2e.com"]},
        headers=teacher_headers,
    )
    assert add_email_res.status_code == 200

    # Teacher retrieves the tutor's unique invitation token.
    tutor_details_res = client.get(
        f"{settings.API_ROOT_PATH}/tutors/{tutor_id}", headers=teacher_headers
    )
    assert tutor_details_res.status_code == 200
    invitation_token = tutor_details_res.json()["token"]

    # Student uses the token to enroll.
    enrollment_res = client.post(
        f"{settings.API_ROOT_PATH}/enrollments",
        json={"invitation_token": invitation_token},
        headers=student_headers,
    )
    assert enrollment_res.status_code == 201

    # Student creates a chat with the Tutor
    student_chat_res = client.post(
        f"{settings.API_ROOT_PATH}/chats",
        json={"tutor_id": tutor_id, "title": "My Private Study Chat"},
        headers=student_headers,
    )
    assert student_chat_res.status_code == 201
    student_chat_id = student_chat_res.json()["id"]

    # Student asks a question in the Chat.
    mock_llm_service = mocker.MagicMock()
    mock_llm = mocker.MagicMock(
        return_value="mocked llm response about multi-head attention"
    )
    mock_llm_service.get_llm.return_value = mock_llm
    app.dependency_overrides[get_llm_service] = lambda: mock_llm_service

    query_res = client.post(
        f"{settings.API_ROOT_PATH}/chats/{student_chat_id}/query",
        json={"query": "What is this document about?"},
        headers=student_headers,
    )
    assert query_res.status_code == 200, f"Query failed: {query_res.json()}"
    assert "mocked llm response" in query_res.json()["answer"]
