#!/usr/bin/env bash
# Validate deployed API health (HTTP and HTTPS).
set -euo pipefail

DOMAIN="${DOMAIN:-}"
STATE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.provision-state.env"

if [[ -f "${STATE_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${STATE_FILE}"
fi

TARGET_HOST="${1:-${DOMAIN:-${PUBLIC_IP:-}}}"
if [[ -z "${TARGET_HOST}" ]]; then
  echo "Pass a host, set DOMAIN, or run provision.sh first."
  exit 1
fi
echo "Checking https://${TARGET_HOST}/health ..."
curl -fsS --max-time 20 "https://${TARGET_HOST}/health"
echo
echo "HTTPS health check passed."
