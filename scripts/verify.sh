#!/bin/sh
# Disposable test project: never reuses the development database or volume.
set -eu
cd "$(dirname "$0")/.."
mode=${1:-all}
case "$mode" in all|backend|frontend|stack|security) ;; *) printf 'Usage: %s [all|backend|frontend|stack|security]\n' "$0" >&2; exit 2 ;; esac
docker info >/dev/null
run_id="$(date +%s)-$$"
project="b2b-test-$run_id"
configuration=$(mktemp -d "${TMPDIR:-/tmp}/b2b-verify.XXXXXX")
export POSTGRES_USER=b2b POSTGRES_DB="b2b_test_$(date +%s)_$$" WEB_PORT=0
export POSTGRES_PASSWORD
POSTGRES_PASSWORD=$(docker run --rm python:3.12.15-slim-bookworm@sha256:7ec4715ec1f0fc9a6d4835b995d2b6e921ea23ff8b354c33f6f9fb82f5882ac7 python -c 'import secrets; print(secrets.token_hex(24))')
export LOGIN_LIMIT=120 DEMO_CREDENTIALS=/dev/null DATABASE_TIMEOUT=10
export ENVIRONMENT=test COOKIE_SECURE=false DEMO_SEED=false PUBLIC_ORIGIN=http://frontend:3000
export JWT_SECRET CSRF_SECRET
JWT_SECRET=$(docker run --rm python:3.12.15-slim-bookworm@sha256:7ec4715ec1f0fc9a6d4835b995d2b6e921ea23ff8b354c33f6f9fb82f5882ac7 python -c 'import secrets; print(secrets.token_hex(32))')
CSRF_SECRET=$(docker run --rm python:3.12.15-slim-bookworm@sha256:7ec4715ec1f0fc9a6d4835b995d2b6e921ea23ff8b354c33f6f9fb82f5882ac7 python -c 'import secrets; print(secrets.token_hex(32))')
export REPORTS_DIR="$(pwd)/reports/$project"
mkdir -p "$REPORTS_DIR/backend" "$REPORTS_DIR/frontend" "$REPORTS_DIR/playwright" "$REPORTS_DIR/security"
export TEST_FIXTURES_DIR="$configuration/fixtures"
mkdir -m 700 "$TEST_FIXTURES_DIR"
: > "$configuration/environment"
compose() { docker compose --env-file "$configuration/environment" --project-name "$project" --profile test "$@"; }
cleanup() {
  result=$1
  trap - 0
  if ! compose down --volumes --remove-orphans; then
    printf 'Failed to clean test project %s\n' "$project" >&2
    result=1
  fi
  rm -rf "$configuration"
  printf 'Verification %s exit=%s; reports: %s\n' "$mode" "$result" "$REPORTS_DIR"
  exit "$result"
}
trap 'cleanup $?' 0
trap 'exit 130' INT
trap 'exit 143' TERM
compose config --quiet
if [ "$mode" = all ] || [ "$mode" = backend ]; then
  compose build backend-test
  compose up --wait --wait-timeout 120 db
  compose run --rm --no-deps backend-test
fi
if [ "$mode" = all ] || [ "$mode" = frontend ]; then
  compose build frontend-test
  compose run --rm --no-deps frontend-test
fi
if [ "$mode" = all ] || [ "$mode" = stack ]; then
  compose build migrate seed backend backend-test frontend e2e
  compose up --wait --wait-timeout 600 db backend frontend
  compose run --rm --no-deps backend-test python -m tests.e2e_fixture
  compose run --rm --no-deps e2e
  # Preserve synthetic data across container replacement; only this test namespace.
  compose exec -T db psql -U b2b -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 \
    -c "CREATE TABLE public.persistence_probe (value text); INSERT INTO public.persistence_probe VALUES ('preserved');"
  compose up --force-recreate --wait --wait-timeout 600 db backend frontend
  actual=$(compose exec -T db psql -U b2b -d "$POSTGRES_DB" -At -v ON_ERROR_STOP=1 -c 'SELECT value FROM public.persistence_probe')
  [ "$actual" = preserved ]
  compose exec -T db psql -U b2b -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c 'DROP TABLE public.persistence_probe'
  compose up --wait --wait-timeout 600 db backend frontend
fi
if [ "$mode" = all ] || [ "$mode" = security ]; then
  compose build backend-test frontend-test
  compose run --rm --no-deps backend-test sh -c 'uv export --frozen --no-emit-project --output-file /tmp/dependencies.txt >/dev/null; pip-audit --strict --disable-pip --no-deps -r /tmp/dependencies.txt --format=json --output /reports/security/python-audit.json'
  compose run --rm --no-deps frontend-test sh -c 'npm audit --audit-level=high --json > /reports/security/npm-audit.json'
  scanner=zricethezav/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f
  # Worktrees share Git metadata outside their .git file. Scan a complete bare clone
  # of local history so Docker never depends on inaccessible host paths.
  git clone --bare --no-hardlinks --quiet "$(pwd)" "$configuration/history.git"
  docker run --rm -v "$configuration/history.git:/history:ro" -v "$REPORTS_DIR/security:/reports" \
    -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0=/history \
    "$scanner" git /history --redact --report-format=json --report-path=/reports/secrets-history.json
  mkdir "$configuration/source"
  git ls-files -z --cached --others --exclude-standard > "$configuration/files"
  tar --null -T "$configuration/files" -cf "$configuration/source.tar"
  tar -xf "$configuration/source.tar" -C "$configuration/source"
  docker run --rm -v "$configuration/source:/source:ro" -v "$REPORTS_DIR/security:/reports" \
    "$scanner" dir /source --redact --report-format=json --report-path=/reports/secrets-source.json
fi
