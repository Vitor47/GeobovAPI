#!/usr/bin/env bash
set -euo pipefail

echo "==> Waiting for PostgreSQL and Redis..."
python scripts/wait_for_services.py

echo "==> Running database setup (tables, roles, superuser)..."
python -m app.commands setup

echo "==> Starting application..."
exec "$@"
