#!/usr/bin/env bash
# Selective GeoBov update. Run on the EC2 host (GitHub Actions and push-update.sh do that).
#
#   sudo bash deploy/aws/update.sh --api
#   sudo bash deploy/aws/update.sh --api --migrate
#   sudo bash deploy/aws/update.sh --postgres --redis --mongo
#   sudo bash deploy/aws/update.sh --all
#
# Data volumes are kept. Postgres, Redis, and Mongo are recreated only when selected.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

APP_DIR="${APP_DIR:-/opt/geobov}"
DEPLOY_DIR="${APP_DIR}/deploy/aws"
COMPOSE_FILE="${DEPLOY_DIR}/docker-compose.prod.yml"

UPDATE_API=false
UPDATE_POSTGRES=false
UPDATE_REDIS=false
UPDATE_MONGO=false
RUN_MIGRATIONS=false

usage() {
  cat <<'EOF'
Usage: update.sh [--api] [--postgres] [--redis] [--mongo] [--migrate] [--all]

  --api        Rebuild and restart the API
  --postgres   Pull and restart Postgres (volume is kept)
  --redis      Pull and restart Redis (volume is kept)
  --mongo      Pull and restart MongoDB (volume is kept)
  --migrate    Run Alembic migrations (upgrade head)
  --all        Update every service and run migrations
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api) UPDATE_API=true ;;
    --postgres) UPDATE_POSTGRES=true ;;
    --redis) UPDATE_REDIS=true ;;
    --mongo) UPDATE_MONGO=true ;;
    --migrate) RUN_MIGRATIONS=true ;;
    --all)
      UPDATE_API=true
      UPDATE_POSTGRES=true
      UPDATE_REDIS=true
      UPDATE_MONGO=true
      RUN_MIGRATIONS=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ "${UPDATE_API}" == false && "${UPDATE_POSTGRES}" == false && "${UPDATE_REDIS}" == false && "${UPDATE_MONGO}" == false && "${RUN_MIGRATIONS}" == false ]]; then
  usage
  exit 1
fi

if [[ ! -f "${DEPLOY_DIR}/.env" ]]; then
  echo "Missing ${DEPLOY_DIR}/.env"
  exit 1
fi

cd "${DEPLOY_DIR}"

data_services=()
[[ "${UPDATE_POSTGRES}" == true ]] && data_services+=(db)
[[ "${UPDATE_REDIS}" == true ]] && data_services+=(redis)
[[ "${UPDATE_MONGO}" == true ]] && data_services+=(mongo)

if [[ ${#data_services[@]} -gt 0 ]]; then
  echo "==> Updating ${data_services[*]}"
  docker compose -f "${COMPOSE_FILE}" pull "${data_services[@]}"
  docker compose -f "${COMPOSE_FILE}" up -d --wait "${data_services[@]}"
fi

if [[ "${UPDATE_API}" == true || "${RUN_MIGRATIONS}" == true ]]; then
  echo "==> Building API image"
  docker compose -f "${COMPOSE_FILE}" build api
fi

if [[ "${RUN_MIGRATIONS}" == true ]]; then
  echo "==> Running migrations (alembic upgrade head)"
  docker compose -f "${COMPOSE_FILE}" up -d --wait db
  docker compose -f "${COMPOSE_FILE}" run --rm --no-deps --entrypoint alembic api upgrade head
fi

if [[ "${UPDATE_API}" == true ]]; then
  echo "==> Restarting API"
  docker compose -f "${COMPOSE_FILE}" up -d --no-deps --force-recreate api
  echo "==> Waiting for API health"
  for _ in $(seq 1 60); do
    if curl -fsS "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
      echo "API is healthy."
      exit 0
    fi
    sleep 5
  done
  echo "API did not become healthy. Check: docker compose -f ${COMPOSE_FILE} logs api"
  exit 1
fi

echo "GeoBov update finished."
