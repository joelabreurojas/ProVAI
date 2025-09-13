from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import RedirectResponse


class AuthRedirectMiddleware(BaseHTTPMiddleware):
    """
    A custom middleware to handle unauthorized access for UI routes.
    If a 401 Unauthorized response is generated for a non-API route,
    this middleware intercepts it and transforms it into a redirect
    to the login page.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        is_ui_route = not request.url.path.startswith("/api")

        if response.status_code == status.HTTP_401_UNAUTHORIZED and is_ui_route:
            return RedirectResponse(url="/auth/login")

        return response
