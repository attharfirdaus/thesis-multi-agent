#!/usr/bin/env bash
# Start the whole stack locally. No containers are involved anywhere in this project.
#
#   ./scripts/dev.sh          start PostgreSQL (if needed), migrate, then run API + web
#
# Ctrl-C stops both application processes; PostgreSQL keeps running as a Homebrew service.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/opt/homebrew/opt/postgresql@18/bin:$HOME/.local/bin:$PATH"

if ! pg_isready -q 2>/dev/null; then
  echo "Starting PostgreSQL 18…"
  brew services start postgresql@18 >/dev/null
  for _ in $(seq 1 30); do pg_isready -q 2>/dev/null && break; sleep 1; done
  pg_isready -q || { echo "PostgreSQL did not come up." >&2; exit 1; }
fi

echo "Applying migrations…"
(cd "$ROOT/backend" && uv run python -m scripts.migrate)

cleanup() { kill 0 2>/dev/null || true; }
trap cleanup EXIT INT TERM

echo "API  → http://localhost:8000/docs"
echo "Web  → http://localhost:3000"
(cd "$ROOT/backend" && uv run uvicorn app.main:app --reload --port 8000) &
(cd "$ROOT/frontend" && npm run dev) &
wait
