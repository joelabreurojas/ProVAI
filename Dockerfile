# Build stage
FROM python:3.13-bookworm AS builder

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock ./


# Dependencies stage - Production
FROM builder AS production_dependencies

RUN uv sync --locked --no-cache


# Dependencies stage - Development
FROM builder AS development_dependencies

RUN uv sync --locked --no-cache --extra ci


# Base stage
FROM python:3.13-slim-bookworm AS base

WORKDIR /app

RUN useradd --create-home appuser
RUN chown -R appuser:appuser /app
USER appuser

COPY ./src src
RUN mkdir -p databases
COPY ./alembic alembic
COPY ./alembic.ini .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000


# Development stage
FROM base AS development

COPY --from=development_dependencies /app/.venv .venv

COPY ./tests tests

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--reload"]


# Production stage
FROM base AS production

COPY --from=production_dependencies /app/.venv .venv

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
