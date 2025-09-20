# ---- Base image (tools + Poetry) ----
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3

# Minimal system deps (curl for Poetry installer)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (no virtualenvs inside containers)
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app

# ---- Builder (make a wheel) ----
FROM base AS builder
# Copy metadata first for better caching
COPY pyproject.toml poetry.lock* ./
# Copy the rest
COPY . .
# Build a wheel in /app/dist
RUN poetry build -f wheel

# ---- Runtime (tiny, non-root) ----
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create unprivileged user
RUN useradd -m -u 10001 appuser
WORKDIR /app

# Copy wheel with its real filename and install it
COPY --from=builder /app/dist/*.whl /tmp/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /tmp/*.whl && \
    rm -f /tmp/*.whl

EXPOSE 8000

# Healthcheck: simple TCP connect to port 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import socket,sys; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1',8000)); s.close()"

USER appuser

# Default command (override in Compose if needed)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
