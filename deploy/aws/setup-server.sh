#!/usr/bin/env bash
# Bootstrap GeoBov on a fresh Ubuntu EC2 (Docker + Nginx + optional Certbot).
# Run as root or with sudo after the repo is on the instance.
set -euo pipefail

DOMAIN="${DOMAIN:-_}"
APP_DIR="${APP_DIR:-/opt/geobov}"
DEPLOY_DIR="${APP_DIR}/deploy/aws"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"
PUBLIC_IP="${PUBLIC_IP:-}"
AWS_REGION="${AWS_REGION:-sa-east-1}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo bash $0"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg nginx unzip

install_aws_cli() {
  if command -v aws >/dev/null 2>&1; then
    return 0
  fi
  local arch pkg
  case "$(uname -m)" in
    aarch64|arm64) arch="aarch64" ;;
    x86_64|amd64) arch="x86_64" ;;
    *)
      echo "No AWS CLI build for $(uname -m). Keeping the env file on disk."
      return 0
      ;;
  esac
  pkg="$(mktemp -d)"
  curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${arch}.zip" -o "${pkg}/awscliv2.zip"
  unzip -q "${pkg}/awscliv2.zip" -d "${pkg}"
  "${pkg}/aws/install" --update
  rm -rf "${pkg}"
}

install_aws_cli

refresh_env_from_ssm() {
  if ! command -v aws >/dev/null 2>&1; then
    echo "AWS CLI missing. Keeping the env file already on disk."
    return 0
  fi
  local tmp
  tmp="$(mktemp)"
  if aws ssm get-parameter \
      --region "${AWS_REGION}" \
      --name /geobov/prod/env \
      --with-decryption \
      --query Parameter.Value \
      --output text | tr -d '\n' | base64 -d > "${tmp}"; then
    if [[ -s "${tmp}" ]]; then
      install -m 600 "${tmp}" "${DEPLOY_DIR}/.env"
      rm -f "${tmp}"
      echo "Loaded environment from SSM Parameter Store."
      return 0
    fi
  fi
  rm -f "${tmp}"
  echo "SSM parameter /geobov/prod/env is not available. Using the env file on disk."
}

mkdir -p "${DEPLOY_DIR}"
refresh_env_from_ssm

if [[ ! -s "${DEPLOY_DIR}/.env" ]]; then
  echo "Missing ${DEPLOY_DIR}/.env and SSM parameter /geobov/prod/env."
  exit 1
fi
chmod 600 "${DEPLOY_DIR}/.env"

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
cp "${DEPLOY_DIR}/nginx/http-only.conf.template" /etc/nginx/sites-available/geobov
ln -sfn /etc/nginx/sites-available/geobov /etc/nginx/sites-enabled/geobov
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

if [[ -z "${CERTBOT_EMAIL}" ]]; then
  echo "CERTBOT_EMAIL is required to request a Let's Encrypt certificate."
  exit 1
fi

if ! command -v certbot >/dev/null 2>&1 || ! certbot --help all 2>/dev/null | grep -q -- '--ip-address'; then
  apt-get install -y snapd
  systemctl enable --now snapd.socket
  snap install core
  snap install --classic certbot
  ln -sf /snap/bin/certbot /usr/bin/certbot
fi

CERT_NAME=""
if [[ -n "${DOMAIN}" && "${DOMAIN}" != "_" ]]; then
  CERT_NAME="${DOMAIN}"
  certbot certonly \
    --webroot -w /var/www/certbot \
    --domain "${CERT_NAME}" \
    --non-interactive \
    --agree-tos \
    -m "${CERTBOT_EMAIL}" \
    --keep-until-expiring \
    --deploy-hook "systemctl reload nginx"
else
  if [[ -z "${PUBLIC_IP}" ]]; then
    echo "Set DOMAIN or PUBLIC_IP so Let's Encrypt can issue a certificate."
    exit 1
  fi
  CERT_NAME="${PUBLIC_IP}"
  certbot certonly \
    --webroot -w /var/www/certbot \
    --ip-address "${PUBLIC_IP}" \
    --preferred-profile shortlived \
    --non-interactive \
    --agree-tos \
    -m "${CERTBOT_EMAIL}" \
    --deploy-hook "systemctl reload nginx"
  echo "IP certificates last about 6 days. Certbot renews them on its timer."
fi

sed "s/DOMAIN_PLACEHOLDER/${CERT_NAME}/g" \
  "${DEPLOY_DIR}/nginx/apigeobov.conf.template" \
  > /etc/nginx/sites-available/geobov
nginx -t && systemctl reload nginx
echo "HTTPS enabled at https://${CERT_NAME}/health"
