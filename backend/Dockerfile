# Multi-service image for lab-api / workers (Render + local compose).
# Build context = repo root. Pin installs from uv lock files.
FROM python:3.12-slim-bookworm

ARG REQUIREMENTS_LOCK=backend/requirements/api.lock.txt

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    LAB_DEFAULT_SEED=42

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements /app/backend/requirements
RUN pip install --no-cache-dir -r "${REQUIREMENTS_LOCK}" \
    && pip install --no-cache-dir PyJWT==2.15.1

COPY labcore /app/labcore
COPY backend /app/backend
COPY pyproject.toml /app/pyproject.toml

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
