#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker info >/dev/null
if [ ! -f .env ]; then
  umask 077
  (set -C; docker run --rm python:3.12.15-slim-bookworm@sha256:7ec4715ec1f0fc9a6d4835b995d2b6e921ea23ff8b354c33f6f9fb82f5882ac7 \
    python -c 'import secrets; print("POSTGRES_PASSWORD=" + secrets.token_hex(24) + "\nPOSTGRES_USER=b2b\nPOSTGRES_DB=b2b_dev\nWEB_PORT=3000")' > .env)
fi
docker compose config --quiet
docker compose up --build --wait --wait-timeout 180 db backend frontend
printf 'Base disponible. UI: http://localhost:%s · API: /api/docs\n' "$(docker compose port frontend 3000 | sed 's/.*://')"
