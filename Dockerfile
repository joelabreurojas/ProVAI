# Build stage
FROM python:3.13-bookworm as builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock .

RUN uv pip install --system .[dev]

# Production stage
FROM python:3.13-slim-bookworm as production

WORKDIR /app

RUN useradd --create-home appuser

RUN chown -R appuser:appuser /app

USER appuser

COPY --from=builder /usr/local/ /usr/local/

COPY ./src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop"]
