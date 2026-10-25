#!/usr/bin/env bash
# Installed in AWS as the GeoBovDeploy document. GitHub cannot change this
# script. It can only ask AWS to run it, with true/false switches.
set -euo pipefail

export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-sa-east-1}"
BUCKET="geobov-deploy-473841056634"
APP_DIR="/opt/geobov"
WORK="/var/lib/geobov"

install -d -m 700 "${WORK}"
rm -rf "${WORK}/release"
install -d -m 700 "${WORK}/release"

aws s3 cp "s3://${BUCKET}/release.tar.gz" "${WORK}/release.tar.gz"
tar -xzf "${WORK}/release.tar.gz" -C "${WORK}/release"
rm -f "${WORK}/release.tar.gz"

# Never replace the server secret, the SSH key, or the provision record.
rsync -a --delete \
  --exclude '.git/' \
  --exclude '.venv/' \
  --exclude 'venv/' \
  --exclude '.env' \
  --exclude '*/.env' \
  --exclude 'deploy/aws/*.pem' \
  --exclude 'deploy/aws/.provision-state.env' \
  "${WORK}/release/" "${APP_DIR}/"
rm -rf "${WORK}/release"

args=()
if [ "{{ updateApi }}" = "true" ]; then args+=(--api); fi
if [ "{{ updatePostgres }}" = "true" ]; then args+=(--postgres); fi
if [ "{{ updateRedis }}" = "true" ]; then args+=(--redis); fi
if [ "{{ updateMongo }}" = "true" ]; then args+=(--mongo); fi
if [ "{{ runMigrations }}" = "true" ]; then args+=(--migrate); fi

if [ "${#args[@]}" -eq 0 ]; then
  echo "No service selected."
  exit 1
fi

bash "${APP_DIR}/deploy/aws/update.sh" "${args[@]}"
