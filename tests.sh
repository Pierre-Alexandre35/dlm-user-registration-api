#!/usr/bin/env bash
set -euo pipefail

echo "Running tests with pytest..."

poetry run pytest -v --tb=short "$@"