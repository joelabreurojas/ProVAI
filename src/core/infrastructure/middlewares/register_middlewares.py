from typing import Any, Tuple

from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.core.infrastructure.settings import settings

from .logging_middleware import logging_middleware

_MIDDLEWARE_STACK: list[Tuple[Any, dict[str, Any]]] = [
    (SessionMiddleware, {"secret_key": settings.SECRET_KEY}),
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
