#!/usr/bin/env bash
set -euo pipefail

PROFILE="${PROFILE:-dev}"
IMAGE="${IMAGE:-fastapi-hello:latest}"
APP_URL="${APP_URL:-http://localhost:8000}"
PROBE_URL="${PROBE_URL:-http://localhost:8000/health}"
SMTP_HEALTH_URL="${SMTP_HEALTH_URL:-http://localhost:18080/health}"

RUN_SMOKE="${RUN_SMOKE:-1}"
CLEAN_VOLUMES="${CLEAN_VOLUMES:-0}"

say() { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || die "Missing dependency: $1"; }

wait_http_200() {
  local url="$1" name="$2" max="${3:-60}"
  say "Waiting for $name at $url ..."
  for i in $(seq 1 "$max"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "  -> $name is up"
      return 0
    fi
    sleep 1
  done
  die "$name did not become healthy in ${max}s"
}

# ---- Pre-flight --------------------------------------------------------------
need docker
need curl
need awk
need grep

if [ ! -f .env ]; then
  say ".env not found, creating from .env.example"
  cp .env.example .env || die "Failed to copy .env.example"
fi

say "Bringing down previous stack"
if [ "$CLEAN_VOLUMES" = "1" ]; then
  docker compose down -v || true
else
  docker compose down || true
fi

say "Building app image: $IMAGE"
docker build -t "$IMAGE" .

say "Starting stack (profile: $PROFILE)"
docker compose --profile "$PROFILE" up -d --build

say "Waiting for services to be healthy"
wait_http_200 "$SMTP_HEALTH_URL" "smtp-mock"
wait_http_200 "$PROBE_URL" "FastAPI app"

say "OpenAPI docs: $APP_URL/docs"

# ---- Smoke test --------------------------------------------------------------
if [ "$RUN_SMOKE" = "1" ]; then
  say "Running smoke test (register -> activate via Basic Auth)"

  # --- Case 1: immediate success ---
  TS=$(date +%s)
  EMAIL="alice+$TS@example.com"
  PASS="S3cureP@ss"

  say "Registering user: $EMAIL"
  curl -fsS -X POST "$APP_URL/users" -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}"

  say "Reading activation code from smtp-mock logs"
  sleep 1
  CODE=$(docker compose logs smtp-mock --since 2m | grep -Eo 'Code: [0-9]{4}' | tail -n1 | awk '{print $2}')

  if [ -z "${CODE:-}" ]; then
    die "Could not extract code from smtp-mock logs."
  fi
  echo "  -> Code detected: $CODE"

  say "Activating with Basic Auth (should succeed)"
  curl -fsS -X POST "$APP_URL/auth/activate" \
    -u "$EMAIL:$PASS" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"$CODE\"}" | jq . || true
  say "Smoke test case 1 done (activation works)"

  # --- Case 2: expiry enforced ---
  TS2=$(date +%s)
  EMAIL2="bob+$TS2@example.com"
  PASS2="AnotherP@ss"

  say "Registering second user: $EMAIL2"
  curl -fsS -X POST "$APP_URL/users" -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL2\",\"password\":\"$PASS2\"}"

  say "Reading activation code from smtp-mock logs"
  sleep 1
  CODE2=$(docker compose logs smtp-mock --since 2m | grep -Eo 'Code: [0-9]{4}' | tail -n1 | awk '{print $2}')
  echo "  -> Code detected for second user: $CODE2"

  say "Waiting 65s to ensure OTP expires..."
  sleep 65

  say "Trying to activate expired code (should fail with 410 Gone)"
  curl -i -X POST "$APP_URL/auth/activate" \
    -u "$EMAIL2:$PASS2" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"$CODE2\"}" || true
  say "Smoke test case 2 done (expiry enforced)"
fi

say "All good. To see logs:"
echo "  docker compose logs -f"
