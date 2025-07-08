# Build stage
FROM python:3.13-bookworm as builder

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml .

COPY uv.lock .

RUN uv venv && uv sync --locked --no-dev --no-cache

# Production stage
FROM python:3.13-slim-bookworm as production

WORKDIR /app

RUN useradd --create-home appuser

RUN chown -R appuser:appuser /app

USER appuser

COPY --from=builder /app/.venv .venv

COPY ./src src

COPY ./alembic alembic

COPY ./alembic.ini .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
