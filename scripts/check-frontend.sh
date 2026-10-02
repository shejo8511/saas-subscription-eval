#!/bin/sh
set -eu
cd /app
npm run lint
npm run format:check
npm run typecheck
npm run test -- --coverage.reportsDirectory=/reports/frontend/coverage
npm run build
