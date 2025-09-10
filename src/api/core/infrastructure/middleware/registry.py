from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.api.core.infrastructure.middleware import logging_middleware
from src.api.core.infrastructure.settings import settings
from src.ui.middleware import AuthRedirectMiddleware

_MIDDLEWARE_STACK = [
    (SessionMiddleware, {"secret_key": settings.SECRET_KEY}),
    (AuthRedirectMiddleware, {}),
    (SlowAPIMiddleware, {}),
    (BaseHTTPMiddleware, {"dispatch": logging_middleware}),
]


def register_middleware(app: FastAPI) -> None:
    """
    Registers all application middleware from the centralized stack.
    This function is the single source of truth for middleware registration.
    """
    for middleware, options in _MIDDLEWARE_STACK:
        app.add_middleware(middleware, **options)
