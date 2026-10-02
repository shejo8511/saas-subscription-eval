#!/bin/sh
set -eu
cd /app
mkdir -p /reports/backend
ruff check . /workspace/scripts
ruff format --check . /workspace/scripts
mypy app
pytest tests/unit tests/integration -o cache_dir=/tmp/pytest_cache --cov=app --cov-branch \
  --cov-report=term-missing --cov-report=json:/reports/backend/coverage.json \
  --cov-report=xml:/reports/backend/coverage.xml --cov-report=html:/reports/backend/html \
  --junitxml=/reports/backend/tests.xml
python /workspace/scripts/check_coverage.py /reports/backend/coverage.json
cd /workspace
python -m unittest discover -s scripts/tests -v
