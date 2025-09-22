FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install deps (include pydantic[email] to get email-validator)
RUN pip install --no-cache-dir fastapi uvicorn "pydantic[email]"

# (optional) curl for your healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]