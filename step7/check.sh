#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PORT=5100

echo "=== Checking Step7 (templates + HTML) on port $PORT ==="

docker compose down -v >/dev/null 2>&1 || true
docker compose up -d --build

echo "Waiting for Flask to be ready..."
for i in $(seq 1 30); do
  if curl -sSf "http://localhost:${PORT}/" >/dev/null 2>&1; then break; fi
  sleep 1
done
echo "Waiting for MySQL (via /db)..."
for i in $(seq 1 45); do
  if curl -sSf "http://localhost:${PORT}/db" | grep -q "MySQL Version:"; then break; fi
  sleep 1
done

echo "- POST /users"
curl -sSf -X POST -d "name=Taro" "http://localhost:${PORT}/users" | grep -q '"name":"Taro"'

echo "- GET /users (JSON)"
curl -sSf "http://localhost:${PORT}/users" | grep -q '"name":"Taro"'

echo "- GET /users/new (HTML form)"
curl -sSf "http://localhost:${PORT}/users/new" | grep -q "ユーザー登録フォーム"

echo "- GET /users/list (HTML table)"
curl -sSf "http://localhost:${PORT}/users/list" | grep -q "ユーザー一覧"

echo "OK: Step7 checks passed."

docker compose down -v

