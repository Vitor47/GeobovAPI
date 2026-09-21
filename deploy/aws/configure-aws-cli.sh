#!/usr/bin/env bash
# Write AWS credentials from environment variables into ~/.aws (Windows symlink ok).
# Usage:
#   export AWS_ACCESS_KEY_ID=AKIA...
#   export AWS_SECRET_ACCESS_KEY=...
#   export AWS_DEFAULT_REGION=sa-east-1
#   bash deploy/aws/configure-aws-cli.sh
set -euo pipefail

AWS_DIR="${AWS_SHARED_CREDENTIALS_FILE:-$HOME/.aws}"
# If symlink, resolve parent
if [[ -L "$HOME/.aws" ]]; then
  AWS_DIR="$(readlink -f "$HOME/.aws" 2>/dev/null || readlink "$HOME/.aws")"
fi
mkdir -p "$AWS_DIR"

REGION="${AWS_DEFAULT_REGION:-${AWS_REGION:-sa-east-1}}"

if [[ -z "${AWS_ACCESS_KEY_ID:-}" || -z "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
  echo "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY first."
  echo "Create keys in AWS Console → IAM → Users → Security credentials → Access keys."
  exit 1
fi

cat > "${AWS_DIR}/credentials" <<EOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF
chmod 600 "${AWS_DIR}/credentials" 2>/dev/null || true

cat > "${AWS_DIR}/config" <<EOF
[default]
region = ${REGION}
output = json
EOF

export PATH="${HOME}/.local/bin:${PATH}"
aws sts get-caller-identity
echo "AWS CLI configured for region ${REGION}."
