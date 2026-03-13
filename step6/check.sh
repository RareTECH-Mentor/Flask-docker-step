#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PORT=5100

echo "=== Checking Step6 (CRUD API) on port $PORT ==="

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
USER_JSON=$(curl -sSf -X POST -d "name=Taro" "http://localhost:${PORT}/users")
echo "$USER_JSON" | python3 -c "import sys, json; d=json.load(sys.stdin); assert d['name']=='Taro'"

USER_ID=$(echo "$USER_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

echo "- GET /users"
curl -sSf "http://localhost:${PORT}/users" | grep -q "\"id\":$USER_ID"

echo "- GET /users/<id>"
curl -sSf "http://localhost:${PORT}/users/$USER_ID" | grep -q "\"id\":$USER_ID"

echo "- DELETE /users/<id>"
curl -sSf -X DELETE "http://localhost:${PORT}/users/$USER_ID" | grep -q "user deleted"

echo "OK: Step6 checks passed."

docker compose down -v

