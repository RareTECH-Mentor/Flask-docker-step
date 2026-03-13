#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PORT=5100

echo "=== Checking Step8 (config + error handling) on port $PORT ==="

docker compose down -v >/dev/null 2>&1 || true
docker compose up -d --build

echo "Waiting for Flask to be ready..."
for i in $(seq 1 30); do
  if curl -sSf "http://localhost:${PORT}/" >/dev/null 2>&1; then break; fi
  sleep 1
done
echo "Waiting for MySQL (via /db)..."
for i in $(seq 1 45); do
  if curl -sf "http://localhost:${PORT}/db" | grep -q "MySQL Version:"; then break; fi
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

echo "- GET /users/99999 (should 404 with JSON error)"
set +e
HTTP_CODE=$(curl -s -o /tmp/step8_notfound_body -w "%{http_code}" "http://localhost:${PORT}/users/99999")
set -e
if [ "$HTTP_CODE" != "404" ]; then
  echo "Expected 404, got $HTTP_CODE"
  cat /tmp/step8_notfound_body
  exit 1
fi
grep -q '"error":"user not found"' /tmp/step8_notfound_body

echo "OK: Step8 checks passed."

docker compose down -v

