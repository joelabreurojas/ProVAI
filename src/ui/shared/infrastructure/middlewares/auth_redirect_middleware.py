from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import RedirectResponse


class AuthRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        is_ui_route = not request.url.path.startswith("/api")
        is_unauthorized = response.status_code == status.HTTP_401_UNAUTHORIZED
        is_auth_route = request.url.path.startswith("/auth")

        # If it's a 401 on a UI page that isn't already an auth page, redirect.
        if is_ui_route and is_unauthorized and not is_auth_route:
            # We will use 303 See Other, which is correct for this action.
            return RedirectResponse(
                url=request.url_for("serve_login_page"),
                status_code=status.HTTP_303_SEE_OTHER,
            )

        return response
