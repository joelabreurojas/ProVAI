import fitz
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture  # <-- Use the correct import
from sqlalchemy.orm import Session

from src.ai.dependencies import get_llm_service
from src.auth.domain.models import User
from src.rag.dependencies import get_rag_vector_store


def test_full_user_flow(
    client: TestClient,
    db_session: Session,
    mocker: MockerFixture,
) -> None:
    """
    Tests the full end-to-end workflow by simulating real API calls and
    mocking external AI services for speed and determinism.

    This test simulates the entire lifecycle of a user interaction:
    1. A Teacher and a Student are registered via the API.
    2. The Teacher logs in and creates a Tutor via the API.
    3. The Teacher creates an invitation for the Tutor.
    4. The Student logs in and uses the invitation to enroll.
    5. The Teacher successfully uploads a valid PDF to the Tutor.
    6. The Student successfully queries the Tutor and receives a mocked response.
    """
    # Register User and promote it as Teacher
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "E2E Teacher",
            "email": "teacher@e2e.com",
            "password": "password123",
            "role": "teacher",
        },
    )
    assert response.status_code == 201, "Teacher registration failed"
    teacher_db = db_session.query(User).filter_by(email="teacher@e2e.com").first()
    assert teacher_db is not None, "Teacher not found in DB after registration"

    # Register User as Student
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "E2E Student",
            "email": "student@e2e.com",
            "password": "password456",
            "role": "student",
        },
    )
    assert response.status_code == 201, "Student registration failed"

    # Teacher logs in
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "teacher@e2e.com", "password": "password123"},
    )
    assert response.status_code == 200, "Teacher login failed"
    teacher_token = response.json()["access_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # Teacher creates a Tutor
    response = client.post(
        "/api/v1/tutors",
        json={"course_name": "E2E Test Course"},
        headers=teacher_headers,
    )
    assert response.status_code == 201, f"Tutor creation failed: {response.json()}"
    tutor_id = response.json()["id"]

    # Teacher creates an Invitation
    response = client.post(
        f"/api/v1/tutors/{tutor_id}/invitations",
        headers=teacher_headers,
    )
    assert response.status_code == 201, f"Invitation creation failed: {response.json()}"
    invitation_token = response.json()["enrollment_token"]

    # Student logs in
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "student@e2e.com", "password": "password456"},
    )
    assert response.status_code == 200, "Student login failed"
    student_token = response.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Student Enrolls in the Tutor
    response = client.post(
        f"/api/v1/tutors/{tutor_id}/enrollments",
        json={"invitation_token": invitation_token},
        headers=student_headers,
    )
    assert response.status_code == 201, f"Enrollment failed: {response.json()}"

    # Teacher uploads Document
    mock_vector_store = mocker.MagicMock()
    client.app.dependency_overrides[get_rag_vector_store] = lambda: mock_vector_store

    # Create a valid PDF file in memory
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "This is a real test PDF about multi-head attention.")
    pdf_bytes = doc.write()
    doc.close()

    response = client.post(
        f"/api/v1/tutors/{tutor_id}/upload",
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")},
        headers=teacher_headers,
    )
    assert response.status_code == 201, f"Document upload failed: {response.json()}"
    mock_vector_store.add_texts.assert_called_once()

    # 5. Student queries
    mock_llm_service = mocker.MagicMock()
    mock_llm = mocker.MagicMock()
    mock_llm.return_value = "mocked llm response about multi-head attention"
    mock_llm_service.get_llm.return_value = mock_llm
    client.app.dependency_overrides[get_llm_service] = lambda: mock_llm_service

    response = client.post(
        f"/api/v1/tutors/{tutor_id}/query",
        params={"query": "What is this document about?"},
        headers=student_headers,
    )
    assert response.status_code == 200, f"Query failed: {response.json()}"
    assert "mocked llm response" in response.json()["answer"]

    # Cleanup
    del client.app.dependency_overrides[get_rag_vector_store]
    del client.app.dependency_overrides[get_llm_service]
