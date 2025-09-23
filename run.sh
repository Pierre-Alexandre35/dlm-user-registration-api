#!/usr/bin/env bash
set -euo pipefail

# ---- Config -----------------------------------------------------------------
PROFILE="${PROFILE:-dev}"                     # dev | prod
IMAGE="${IMAGE:-fastapi-hello:latest}"        # Docker image tag for the app
APP_URL="${APP_URL:-http://localhost:8000}" # FastAPI base URL (business endpoints under /v1)
PROBE_URL="${PROBE_URL:-http://localhost:8000/health}" # Health endpoint is unprefixed
SMTP_HEALTH_URL="${SMTP_HEALTH_URL:-http://localhost:18080/health}" # host-mapped

CLEAN_VOLUMES="${CLEAN_VOLUMES:-0}"           # 1 = docker compose down -v

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

say "All services up ✅"
echo "You can now test the API manually or via Swagger."
