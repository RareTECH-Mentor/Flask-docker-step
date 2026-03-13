#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PORT=5100

echo "=== Checking Step5 (Docker + Flask + MySQL) on port $PORT ==="

docker compose down -v >/dev/null 2>&1 || true
docker compose up -d --build

echo "Waiting for Flask to be ready..."
for i in $(seq 1 30); do
  if curl -sSf "http://localhost:${PORT}/" >/dev/null 2>&1; then break; fi
  sleep 1
done
echo "Waiting for MySQL (via /db)..."
for i in $(seq 1 45); do
  if curl -s "http://localhost:${PORT}/db" 2>/dev/null | grep -q "MySQL Version:"; then break; fi
  sleep 1
done

echo "- / endpoint"
curl -sSf "http://localhost:${PORT}/" | grep -q "Hello Docker Flask + MySQL"

echo "- /db endpoint"
curl -sSf "http://localhost:${PORT}/db" | grep -q "MySQL Version:"

echo "OK: Step5 checks passed."

docker compose down -v

