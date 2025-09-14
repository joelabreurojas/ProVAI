from typing import Any, Tuple

from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.core.infrastructure.settings import settings

from .logging_middleware import logging_middleware

is_prod = settings.ENV_STATE == "prod"
session_middleware_options = {
    "secret_key": settings.SECRET_KEY,
    "https_only": is_prod,  # Only send cookie over HTTPS in production
    "same_site": "lax",  # Recommended setting for most apps
}

_MIDDLEWARE_STACK: list[Tuple[Any, dict[str, Any]]] = [
    (SessionMiddleware, session_middleware_options),
    (SlowAPIMiddleware, {}),
    (BaseHTTPMiddleware, {"dispatch": logging_middleware}),
]


def register_middlewares(app: FastAPI, extra: list[Tuple[Any, dict[str, Any]]]) -> None:
    """
    Registers all application middleware from the centralized stack.
    """
    middleware_stack = _MIDDLEWARE_STACK + extra
    for middleware, options in reversed(middleware_stack):
        app.add_middleware(middleware, **options)
