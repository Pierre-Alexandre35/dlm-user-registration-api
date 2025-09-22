## Project Overview

A containerized micro-service implementing user registration and activation.
Users register with email + password, receive a 4-digit code via email, and activate their account within 1 minute using Basic Auth.

## Tools used

- PSQL: Database (2 tables)
- Psycopg3: low-level PostgreSQL driver (no ORM)
- Pydantic: Request/response validation and serialization
- Argon2-cffi: secure password hashing
- httpx: async HTTP client to interact with the external SMTP service

## PSQL tables schemas:

`users` Table

Stores registered users.

| Column          | Type        | Description                      |
| --------------- | ----------- | -------------------------------- |
| `id`            | BIGSERIAL   | Primary key                      |
| `email`         | CITEXT      | Unique, case-insensitive email   |
| `password_hash` | TEXT        | Hashed password                  |
| `is_active`     | BOOLEAN     | Whether the account is activated |
| `created_at`    | TIMESTAMPTZ | Timestamp of user creation       |
| `updated_at`    | TIMESTAMPTZ | Timestamp of last update         |

`activation_tokens` Table

Stores 4-digit activation tokens (hashed) linked to users.

| Column        | Type        | Description                        |
| ------------- | ----------- | ---------------------------------- |
| `id`          | BIGSERIAL   | Primary key                        |
| `user_id`     | BIGINT      | Foreign key → `users(id)`          |
| `code_hash`   | TEXT        | Argon2 hash of the 4-digit OTP     |
| `created_at`  | TIMESTAMPTZ | When the token was created         |
| `expires_at`  | TIMESTAMPTZ | Expiration timestamp               |
| `consumed_at` | TIMESTAMPTZ | When the token was used (nullable) |

docker build -t fastapi-hello:latest .

docker run --rm -p 8000:8000 fastapi-hello:latest \
 gunicorn app.main:app -k uvicorn.workers.UvicornWorker \
 --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 60

or

docker compose --profile dev up --build

TEST SERVER DE LOGS:

docker compose build smtp-mock  
docker compose --profile dev up -d
docker compose logs -f smtp-mock

curl -X POST http://localhost:18080/send \
 -H "Content-Type: application/json" \
 -d '{"to":"alice@example.com","subject":"Your code","body":"Code: 1334"}'
{"status":"sent"}%

## project layout

```
.
├── app/                  # FastAPI source
│   ├── routers/          # Routers: auth, users
│   ├── crud/             # Repos: users_repo, tokens_repo
│   ├── services/         # smtp_client (3rd-party mock)
│   ├── core/security.py  # Argon2id + OTP
│   ├── db/cursor.py      # psycopg3 connection
│   └── main.py           # FastAPI entrypoint
├── migrations/           # SQL migrations
│   └── 001_init.up.sql
├── smtp-mock/            # Fake SMTP server (logs code)
│   ├── main.py
│   └── Dockerfile
├── docker-compose.yml
├── Dockerfile            # FastAPI app
├── pyproject.toml
├── poetry.lock
├── run.sh                # Orchestration + smoke test
└── README.md
```
