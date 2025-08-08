# Build stage
FROM ghcr.io/astral-sh/uv:0.8.3-python3.13-bookworm-slim AS builder

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	build-essential \
	&& rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_HTTP_TIMEOUT=1200


# Dependencies stage - Production
FROM builder AS production_dependencies

RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
	--mount=type=bind,source=uv.lock,target=uv.lock \
	uv sync --frozen --no-install-project --no-dev --no-editable


# Dependencies stage - Development
FROM builder AS development_dependencies

RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
	--mount=type=bind,source=uv.lock,target=uv.lock \
	uv sync --frozen --no-install-project --extra dev


# Base stage 
FROM python:3.13-slim-bookworm AS base

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	libgomp1 \
	&& rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH"

COPY ./src ./src
COPY ./alembic ./alembic
COPY ./alembic.ini .
COPY ./scripts ./scripts

RUN mkdir -p databases models sample_data vector_store scripts

RUN useradd --create-home appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000


# Development stage
FROM base AS development

COPY --from=development_dependencies /app/.venv .venv

COPY ./tests tests

CMD ["uvicorn", "src.core.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--reload"]


# Production stage
FROM base AS production

COPY --from=production_dependencies /app/.venv .venv

CMD ["uvicorn", "src.core.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
