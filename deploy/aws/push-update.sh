#!/usr/bin/env bash
# Sync this checkout to the GeoBov EC2 and run deploy/aws/update.sh there.
#
#   bash deploy/aws/push-update.sh --api --migrate
#   bash deploy/aws/push-update.sh --postgres
#
# Requires deploy/aws/.provision-state.env from provision.sh and the .pem key.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOY_DIR="${ROOT_DIR}/deploy/aws"
STATE_FILE="${DEPLOY_DIR}/.provision-state.env"

if [[ ! -f "${STATE_FILE}" ]]; then
  echo "Missing ${STATE_FILE}. Run deploy/aws/provision.sh once before updating."
  exit 1
fi

# shellcheck disable=SC1090
source "${STATE_FILE}"

APP_DIR="${APP_DIR:-/opt/geobov}"
KEY_FILE="${KEY_FILE:-${DEPLOY_DIR}/${KEY_NAME:-geobov}.pem}"
PUBLIC_IP="${PUBLIC_IP:-}"

if [[ -z "${PUBLIC_IP}" ]]; then
  echo "PUBLIC_IP is empty in ${STATE_FILE}"
  exit 1
fi
if [[ ! -f "${KEY_FILE}" ]]; then
  echo "SSH key not found: ${KEY_FILE}"
  exit 1
fi

SSH_OPTS=(-i "${KEY_FILE}" -o StrictHostKeyChecking=accept-new)

echo "==> Uploading GeoBov to ubuntu@${PUBLIC_IP}:${APP_DIR}"
ssh "${SSH_OPTS[@]}" "ubuntu@${PUBLIC_IP}" "sudo mkdir -p ${APP_DIR} && sudo chown ubuntu:ubuntu ${APP_DIR}"
rsync -az --delete \
  --exclude '.git' \
  --exclude 'venv' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.mypy_cache' \
  --exclude '.pytest_cache' \
  --exclude '.env' \
  --exclude 'deploy/aws/.env' \
  --exclude 'deploy/aws/*.pem' \
  --exclude 'deploy/aws/.provision-state.env' \
  -e "ssh -i ${KEY_FILE} -o StrictHostKeyChecking=accept-new" \
  "${ROOT_DIR}/" "ubuntu@${PUBLIC_IP}:${APP_DIR}/"

echo "==> Running update on the server: $*"
ssh "${SSH_OPTS[@]}" "ubuntu@${PUBLIC_IP}" \
  "sudo APP_DIR=${APP_DIR} bash ${APP_DIR}/deploy/aws/update.sh $*"
