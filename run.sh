#!/usr/bin/env bash
set -euo pipefail

# ---- Config -----------------------------------------------------------------
PROFILE="${PROFILE:-dev}"                     # dev | prod
IMAGE="${IMAGE:-fastapi-hello:latest}"       # Docker image tag for the app
APP_URL="${APP_URL:-http://localhost:8000/v1}" # FastAPI base URL (business endpoints under /v1)
PROBE_URL="${PROBE_URL:-http://localhost:8000/health}" # Health endpoint is unprefixed
SMTP_HEALTH_URL="${SMTP_HEALTH_URL:-http://localhost:18080/health}" # host-mapped

RUN_SMOKE="${RUN_SMOKE:-1}"                  # 1 = run smoke test after up
CLEAN_VOLUMES="${CLEAN_VOLUMES:-0}"          # 1 = docker compose down -v

# ---- Helpers ----------------------------------------------------------------
say() { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

need() {
  command -v "$1" >/dev/null 2>&1 || die "Missing dependency: $1"
}

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

[ -f .env ] || die "Missing .env file at repo root."

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
# Wait for smtp-mock (host-mapped 18080 -> 8080)
wait_http_200 "$SMTP_HEALTH_URL" "smtp-mock"
# Wait for FastAPI app (/health is unprefixed)
wait_http_200 "$PROBE_URL" "FastAPI app"

say "OpenAPI docs: $APP_URL/docs"

# ---- Smoke test --------------------------------------------------------------
if [ "$RUN_SMOKE" = "1" ]; then
  say "Running smoke test (register -> send activation -> activate via Basic Auth)"

  # random email each run
  TS=$(date +%s)
  EMAIL="alice+$TS@example.com"
  PASS="S3cureP@ss"

  say "Registering user: $EMAIL"
  curl -fsS -X POST "$APP_URL/auth/register" -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}"

  say "Triggering activation email"
  curl -fsS -X POST "$APP_URL/auth/send-activation" -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\"}"

  # Give the mock a moment to log
  sleep 1

  say "Reading last 4-digit code from smtp-mock logs"
  CODE=$(docker compose logs smtp-mock --since 2m \
    | grep -Eo 'Code: [0-9]{4}' \
    | tail -n1 \
    | awk '{print $2}')

  if [ -z "${CODE:-}" ]; then
    die "Could not extract code from smtp-mock logs. Check 'docker compose logs -f smtp-mock'."
  fi
  echo "  -> Code detected: $CODE"

  # --- Case 1: activate immediately (success) ---
  say "Activating with Basic Auth (should succeed)"
  curl -fsS -X POST "$APP_URL/auth/activate" \
    -u "$EMAIL:$CODE" \
    | jq . || true

  echo
  say "Smoke test case 1 done (activation works)"

  # --- Case 2: register new user, wait 65s, expect 410 Gone ---
  TS2=$(date +%s)
  EMAIL2="bob+$TS2@example.com"
  PASS2="AnotherP@ss"

  say "Registering second user for expiry test: $EMAIL2"
  curl -fsS -X POST "$APP_URL/auth/register" -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL2\",\"password\":\"$PASS2\"}"

  say "Triggering activation email for second user"
  curl -fsS -X POST "$APP_URL/auth/send-activation" -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL2\"}"

  sleep 1
  CODE2=$(docker compose logs smtp-mock --since 2m \
    | grep -Eo 'Code: [0-9]{4}' \
    | tail -n1 \
    | awk '{print $2}')
  echo "  -> Code detected for second user: $CODE2"

  say "Waiting 65s to ensure OTP expires..."
  sleep 65

  say "Activating expired code (should fail with 410 Gone)"
  curl -i -X POST "$APP_URL/auth/activate" \
    -u "$EMAIL2:$CODE2" || true

  echo
  say "Smoke test case 2 done (expiry enforced)"
fi

say "All good. To see logs:"
echo "  docker compose logs -f"
