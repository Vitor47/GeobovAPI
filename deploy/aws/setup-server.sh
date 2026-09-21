#!/usr/bin/env bash
# Bootstrap CowTrack API on a fresh Ubuntu EC2 (Docker + Nginx + Certbot).
# Run as root or with sudo after the repo is on the instance.
set -euo pipefail

DOMAIN="${DOMAIN:-apigeobov.com}"
APP_DIR="${APP_DIR:-/opt/cowtrack}"
DEPLOY_DIR="${APP_DIR}/deploy/aws"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo bash $0"
  exit 1
fi

if [[ ! -f "${DEPLOY_DIR}/.env" ]]; then
  echo "Missing ${DEPLOY_DIR}/.env — copy .env.production.example and fill secrets first."
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg nginx certbot python3-certbot-nginx

if ! command -v docker >/dev/null 2>&1; then
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

systemctl enable --now docker nginx

mkdir -p /var/www/certbot
sed "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" \
  "${DEPLOY_DIR}/nginx/http-only.conf.template" \
  > /etc/nginx/sites-available/cowtrack
ln -sfn /etc/nginx/sites-available/cowtrack /etc/nginx/sites-enabled/cowtrack
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

cd "${DEPLOY_DIR}"
docker compose -f docker-compose.prod.yml pull || true
docker compose -f docker-compose.prod.yml up -d --build

echo "==> Waiting for API health on localhost:8000..."
for i in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
    echo "API is healthy."
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "API did not become healthy in time. Check: docker compose -f docker-compose.prod.yml logs"
    exit 1
  fi
  sleep 5
done

if [[ -n "${CERTBOT_EMAIL}" ]]; then
  certbot --nginx \
    -d "${DOMAIN}" \
    --non-interactive \
    --agree-tos \
    -m "${CERTBOT_EMAIL}" \
    --redirect
  sed "s/DOMAIN_PLACEHOLDER/${DOMAIN}/g" \
    "${DEPLOY_DIR}/nginx/apigeobov.conf.template" \
    > /etc/nginx/sites-available/cowtrack
  nginx -t && systemctl reload nginx
  echo "HTTPS enabled for https://${DOMAIN}"
else
  echo "CERTBOT_EMAIL not set — skipping HTTPS. HTTP proxy is active on port 80."
  echo "Later run: CERTBOT_EMAIL=you@email.com DOMAIN=${DOMAIN} bash ${DEPLOY_DIR}/setup-server.sh"
fi

echo "Done. Health: http://${DOMAIN}/health (or https after Certbot)."
