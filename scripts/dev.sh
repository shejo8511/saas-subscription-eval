#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker info >/dev/null
docker run --rm --user "$(id -u):$(id -g)" -v "$(pwd):/workspace" -w /workspace \
  python:3.12.15-slim-bookworm@sha256:7ec4715ec1f0fc9a6d4835b995d2b6e921ea23ff8b354c33f6f9fb82f5882ac7 \
  python scripts/local_config.py
export PUBLIC_ORIGIN="http://localhost:${WEB_PORT:-$(sed -n 's/^WEB_PORT=//p' .env)}"
docker compose config --quiet
docker compose up --build --wait --wait-timeout 180 db seed backend frontend
printf 'Base disponible. UI: http://localhost:%s · API: /api/docs\n' "$(docker compose port frontend 3000 | sed 's/.*://')"
printf 'Credenciales demo locales: .local/demo-credentials.json (no compartir).\n'
