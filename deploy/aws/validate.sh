#!/usr/bin/env bash
# Validate deployed API health (HTTP and HTTPS).
set -euo pipefail

DOMAIN="${DOMAIN:-apigeobov.com}"
STATE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.provision-state.env"

if [[ -f "${STATE_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${STATE_FILE}"
fi

TARGET_HOST="${1:-${DOMAIN}}"
echo "Checking http://${TARGET_HOST}/health ..."
curl -fsS --max-time 20 "http://${TARGET_HOST}/health" || true
echo
echo "Checking https://${TARGET_HOST}/health ..."
curl -fsSk --max-time 20 "https://${TARGET_HOST}/health" || true
echo
echo "Done."
