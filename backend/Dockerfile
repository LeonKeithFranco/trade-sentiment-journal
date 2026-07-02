FROM ghcr.io/astral-sh/uv:latest AS uv

# === Builder stage ===
FROM python:3.12-slim AS builder

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
COPY backend/pyproject.toml backend/pyproject.toml
COPY frontend/pyproject.toml frontend/pyproject.toml
COPY dl/pyproject.toml ml/pyproject.toml

RUN uv sync --frozen --no-dev --package backend

# === Runtime stage ===
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv

COPY backend/ backend/
COPY dl/ dl/

EXPOSE 8000

WORKDIR /app/backend

ENV PATH="/app/.venv/bin:$PATH"

CMD ["fastapi", "run", "app/main.py"]
