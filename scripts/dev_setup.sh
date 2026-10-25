#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing dependencies..."
uv sync --frozen

echo "==> Running project setup (tables, roles, superuser)..."
uv run python -m app.commands setup

echo ""
echo "Setup complete!"
echo "Superuser credentials (from .env):"
echo "  SUPERUSER_EMAIL / SUPERUSER_PASSWORD"
echo ""
echo "Useful commands:"
echo "  uv run python -m app.commands create-company --name 'Farm Name'"
echo "  uv run python -m app.commands create-farmer --full-name 'John' --email farmer@farm.com --password secret --birth-date 1990-01-01 --company-id 1"
echo "  uv run python -m app.commands create-cattle --tag TAG-001 --company-id 1"
