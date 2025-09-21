# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install Poetry
RUN apt-get update && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/* \
  && curl -sSL https://install.python-poetry.org | python3 - \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry


# Install runtime deps (from Poetry export)
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir --upgrade pip \
 && poetry config virtualenvs.create false \
 && poetry install --only main --no-root --no-interaction --no-ansi

# (Code is bind-mounted by docker compose in dev)
# COPY app ./app

# Non-root (optional)
RUN useradd -m -u 10001 appuser
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
