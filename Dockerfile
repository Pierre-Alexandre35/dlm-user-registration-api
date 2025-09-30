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

# Copy dependency files first (better caching)
COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir --upgrade pip \
 && poetry config virtualenvs.create false \
 && poetry install --only main --no-root --no-interaction --no-ansi

# 👇 Copy your actual app code and migrations
COPY app ./app
COPY migrations ./migrations

RUN useradd -m -u 10001 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
