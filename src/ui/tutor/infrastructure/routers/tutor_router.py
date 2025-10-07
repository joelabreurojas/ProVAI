import json
from typing import Any

import httpx
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import ValidationError

from src.core.application.exceptions import AppException
from src.core.application.protocols import (
    ChatServiceProtocol,
    TutorServiceProtocol,
)
from src.core.domain.models import User
from src.core.domain.schemas import TutorUpdate
from src.ui.shared.infrastructure.dependencies import (
    get_authenticated_bff_api_client,
    get_current_user_from_cookie,
    get_sidebar_context,
    validate_csrf_token,
)
from src.ui.shared.infrastructure.utils import htmx_trigger, render_template

router = APIRouter(
    prefix="/tutors", tags=["UI - Tutor Workspace"], include_in_schema=False
)


@router.get("/{tutor_id}")
async def serve_tutor_workspace(
    request: Request,
    tutor_id: int,
    sidebar_context: dict[str, Any] = Depends(get_sidebar_context),
    tutor_service: TutorServiceProtocol = Depends(),
    user: User = Depends(get_current_user_from_cookie),
) -> Response:
    """Serves the main three-panel workspace for a given Tutor/Assistant."""

    toast_message = request.session.pop("toast_message", None)
    toast_category = request.session.pop("toast_category", "success")

    tutor = tutor_service.verify_user_can_access_tutor(tutor_id, user)
    context = {
        "user": user,
        "request": request,
        "title": f"Workspace: {tutor.course_name}",
        "active_tutor_id": tutor.id,
        "tutor": tutor,
        "show_contextual_sidebar": True,
        "contextual_sidebar_url": f"/tutors/{tutor.id}/contextual-sidebar",
        "toast_message": toast_message,
        "toast_category": toast_category,
        **sidebar_context,
    }
    return render_template("tutor/tutor_workspace.html", context)


@router.get("/{tutor_id}/chats-panel")
async def get_chats_panel(
    request: Request,
    tutor_id: int,
    user: User = Depends(get_current_user_from_cookie),
    chat_service: ChatServiceProtocol = Depends(),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Renders the HTML partial for the Chat Management Hub."""
    tutor = tutor_service.verify_user_can_access_tutor(tutor_id, user)
    chats = chat_service.get_chats_for_user_and_tutor(tutor_id, user)
    chats_json = json.dumps(
        [
            {"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()}
            for c in chats
        ]
    )
    context = {
        "request": request,
        "user": user,
        "tutor": tutor,
        "chats_json": chats_json,
    }
    response = render_template("partials/tutor/_chats_panel.html", context)

    events = {"updateChats": json.loads(chats_json)}
    return htmx_trigger(response, events=events, request=request)


@router.get("/{tutor_id}/contextual-sidebar")
async def get_contextual_sidebar(
    request: Request,
    tutor_id: int,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Renders the HTML partial for the Contextual Management Panel."""
    tutor = tutor_service.verify_user_can_access_tutor(tutor_id, user)
    context = {
        "user": user,
        "request": request,
        "tutor": tutor,
    }
    response = render_template("partials/tutor/_contextual_sidebar.html", context)

    return htmx_trigger(response, events={}, request=request)


@router.post("/create-chat/{tutor_id}")
async def handle_create_chat(
    request: Request,
    tutor_id: int,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """
    BFF for creating a new chat. On success, it returns an HX-Redirect header
    that forces a full-page redirect to the new chat's workspace.
    """
    tutor_service.verify_user_can_access_tutor(tutor_id, user)

    async with authenticated_client_manager as client:
        # We'll give the new chat a more descriptive default name
        api_response = await client.post(
            "/chats", json={"tutor_id": tutor_id, "title": "New Conversation"}
        )
    api_response.raise_for_status()
    new_chat_id = api_response.json()["id"]

    # This response is empty, but carries the redirect instruction in its headers.
    response = Response()

    # THE FIX: HX-Redirect tells HTMX to do a full window.location redirect.
    # We will redirect to the full page for the new chat.
    response.headers["HX-Redirect"] = f"/chats/{new_chat_id}"

    return response


@router.get("/{tutor_id}/edit-form")
async def get_tutor_edit_form(
    request: Request,
    tutor_id: int,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Renders the HTML partial for the inline tutor edit form."""
    tutor = tutor_service.verify_user_is_tutor_owner(tutor_id, user)
    context = {"request": request, "user": user, "tutor": tutor}

    response = render_template("partials/tutor/_edit_tutor_form.html", context)
    return htmx_trigger(response, events={}, request=request)


@router.post("/{tutor_id}/edit")
async def handle_edit_tutor_form(
    request: Request,
    tutor_id: int,
    course_name: str = Form(...),
    description: str | None = Form(None),
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for editing a tutor, with robust validation and error handling."""

    try:
        tutor_update = TutorUpdate(course_name=course_name, description=description)

        updated_tutor = tutor_service.update_tutor(
            tutor_id=tutor_id,
            tutor_update=tutor_update,
            requesting_user=user,
        )

        new_title = f"Workspace: {updated_tutor.course_name}"
        context = {
            "user": user,
            "request": request,
            "toast_category": "success",
            "toast_message": "Assistant updated successfully!",
        }
        events = {
            "refreshContextualSidebar": "true",
            "refreshTutorList": "true",
            "updateTitle": {"title": new_title},
        }
        toast = render_template("partials/_toast.html", context)
        return htmx_trigger(toast, events=events, request=request)

    except ValidationError as e:
        clean_msg = (
            e.errors()[0]["msg"].removeprefix("Value error, ").replace("String", "Name")
        )
        context = {
            "user": user,
            "request": request,
            "toast_category": "error",
            "toast_message": clean_msg,
        }
        toast = render_template("partials/_toast.html", context)
        return htmx_trigger(toast, events={}, request=request)

    except AppException as e:
        context = {
            "user": user,
            "request": request,
            "toast_category": "error",
            "toast_message": e.message,
        }
        toast = render_template("partials/_toast.html", context)
        return htmx_trigger(toast, events={}, request=request)


@router.post("/{tutor_id}/delete")
async def handle_delete_tutor(
    request: Request,
    tutor_id: int,
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for deleting a tutor. Sets a flash message and redirects to the dashboard."""
    try:
        async with authenticated_client_manager as client:
            api_response = await client.delete(f"/tutors/{tutor_id}")
        api_response.raise_for_status()

        request.session["toast_message"] = "Assistant deleted successfully."
        request.session["toast_category"] = "success"

    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", "Failed to delete assistant.")
            request.session["toast_message"] = detail
        except Exception:
            request.session["toast_message"] = "An unknown API error occurred."

        request.session["toast_category"] = "error"

    # Now, with the session message set, we redirect.
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{tutor_id}/unenroll")
async def handle_unenroll_tutor(
    request: Request,
    tutor_id: int,
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for unenrolling from a tutor. Sets a flash message and redirects."""
    try:
        async with authenticated_client_manager as client:
            api_response = await client.delete(f"/enrollments/tutors/{tutor_id}")

        api_response.raise_for_status()

        request.session["toast_message"] = "Successfully unenrolled from the tutor."
        request.session["toast_category"] = "success"

    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", "Failed to unenroll.")
            request.session["toast_message"] = detail
        except Exception:
            request.session["toast_message"] = "An unknown API error occurred."

        request.session["toast_category"] = "error"

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{tutor_id}/upload-document")
async def handle_upload_document_form(
    request: Request,
    tutor_id: int,
    file: UploadFile = File(...),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    try:
        files = {"file": (file.filename, await file.read(), file.content_type)}

        async with authenticated_client_manager as client:
            api_response = await client.post(
                f"/tutors/{tutor_id}/documents", files=files
            )

        api_response.raise_for_status()

        request.session["toast_message"] = "Document uploaded successfully!"
        request.session["toast_category"] = "success"

    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", "File upload failed.")
            request.session["toast_message"] = detail
        except Exception:
            request.session["toast_message"] = "An unknown API error occurred."

        request.session["toast_category"] = "error"

    response = Response(status_code=200)

    response.headers["HX-Refresh"] = "true"

    return response


@router.get("/{tutor_id}/documents/{document_id}/download")
async def handle_download_document(
    tutor_id: int,
    document_id: int,
    user: User = Depends(get_current_user_from_cookie),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
) -> Response:
    """
    BFF endpoint that acts as a secure proxy to stream a document from the API.
    """
    async with authenticated_client_manager as client:
        async with client.stream(
            "GET",
            f"/tutors/{tutor_id}/documents/{document_id}/download",
        ) as api_response:
            if api_response.is_error:
                error_text = await api_response.aread()
                return Response(
                    content=f"Error: {api_response.status_code} {error_text.decode()}",
                    status_code=api_response.status_code,
                )

            content_disposition = api_response.headers.get("content-disposition")
            filename = "download.pdf"
            if content_disposition:
                try:
                    filename = content_disposition.split("filename=")[1].strip('"')
                except IndexError:
                    pass

            file_bytes = await api_response.aread()

            def file_stream():
                yield file_bytes

            return StreamingResponse(
                file_stream(),
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )


@router.post("/{tutor_id}/documents/{document_id}/delete")
async def handle_delete_document(
    request: Request,
    tutor_id: int,
    document_id: int,
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for deleting a document link. On success or failure, it sets a
    flash message and forces a full page reload by redirecting."""

    redirect_url = f"/tutors/{tutor_id}"

    try:
        async with authenticated_client_manager as client:
            api_response = await client.delete(
                f"/tutors/{tutor_id}/documents/{document_id}"
            )

        api_response.raise_for_status()

        request.session["toast_message"] = "Document removed successfully!"
        request.session["toast_category"] = "success"

    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", "Failed to remove document.")
            request.session["toast_message"] = detail
        except Exception:
            request.session["toast_message"] = "An unknown API error occurred."

        request.session["toast_category"] = "error"

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{tutor_id}/authorized-students")
async def get_authorized_students_list(
    request: Request,
    tutor_id: int,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Renders the HTML partial for the list of authorized students."""
    tutor = tutor_service.verify_user_is_tutor_owner(tutor_id, user)
    authorized_emails = [auth.student_email for auth in tutor.authorized_students]

    context = {
        "user": user,
        "request": request,
        "tutor": tutor,
        "authorized_emails": sorted(authorized_emails),
    }
    return render_template("partials/tutor/_authorized_students_list.html", context)


@router.get("/{tutor_id}/share-modal-content")
async def get_share_modal_content(
    request: Request,
    tutor_id: int,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
) -> Response:
    """Renders the full inner content for the share access modal."""
    tutor = tutor_service.verify_user_is_tutor_owner(tutor_id, user)

    authorized_emails = [auth.student_email for auth in tutor.authorized_students]

    context = {
        "request": request,
        "user": user,
        "tutor": tutor,
        "authorized_emails": sorted(authorized_emails),
    }
    response = render_template("partials/tutor/_share_access_content.html", context)

    return htmx_trigger(response, events={}, request=request)


@router.post("/{tutor_id}/share")
async def handle_add_authorized_students(
    request: Request,
    tutor_id: int,
    emails: str = Form(...),
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for adding new students. On success, returns the updated list."""
    email_list = [
        email.strip()
        for email in emails.replace(",", "\n").split("\n")
        if email.strip()
    ]

    try:
        if email_list:
            async with authenticated_client_manager as client:
                api_response = await client.post(
                    f"/tutors/{tutor_id}/authorized-emails", json={"emails": email_list}
                )
            api_response.raise_for_status()

    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Failed to add students.")
        context = {
            "user": user,
            "request": request,
            "toast_category": "error",
            "toast_message": detail,
        }
        toast = render_template("partials/_toast.html", context)
        return htmx_trigger(toast, events={}, request=request)

    response = await get_authorized_students_list(
        request, tutor_id, user, tutor_service
    )

    return htmx_trigger(response, events={}, request=request)


@router.post("/{tutor_id}/authorized-emails/{student_email}/delete")
async def handle_remove_authorized_student(
    request: Request,
    tutor_id: int,
    student_email: str,
    user: User = Depends(get_current_user_from_cookie),
    tutor_service: TutorServiceProtocol = Depends(),
    authenticated_client_manager: httpx.AsyncClient = Depends(
        get_authenticated_bff_api_client
    ),
    _csrf: None = Depends(validate_csrf_token),
) -> Response:
    """BFF for removing an authorized student. Returns the updated list on success."""

    try:
        tutor_service.verify_user_is_tutor_owner(tutor_id, user)

        async with authenticated_client_manager as client:
            api_response = await client.delete(
                f"/tutors/{tutor_id}/authorized-emails/{student_email}"
            )
        api_response.raise_for_status()

    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Failed to remove student.")
        context = {
            "user": user,
            "request": request,
            "toast_category": "error",
            "toast_message": detail,
        }
        toast = render_template("partials/_toast.html", context)
        return htmx_trigger(toast, events={}, request=request)

    response = await get_authorized_students_list(
        request, tutor_id, user, tutor_service
    )

    return htmx_trigger(response, events={}, request=request)
