FROM ghcr.io/astral-sh/uv:latest AS uv

# === Builder stage ===
FROM python:3.12-slim AS builder

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
COPY frontend/pyproject.toml frontend/pyproject.toml

RUN uv sync --frozen --no-dev --package frontend

# === Runtime stage ===
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv

COPY frontend/ frontend/

EXPOSE 8501

WORKDIR /app/frontend

ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PATH="/app/.venv/bin:$PATH"

CMD ["streamlit", "run", "main.py"]
