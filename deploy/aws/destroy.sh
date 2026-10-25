#!/usr/bin/env bash
# Stop GeoBov from consuming AWS credits.
# Deletes the instance, releases the Elastic IP, and removes the security group.
#
#   CONFIRM=geobov bash deploy/aws/destroy.sh
set -euo pipefail

if [[ "${CONFIRM:-}" != "geobov" ]]; then
  echo "This deletes the GeoBov EC2 instance, its Elastic IP, and its security group."
  echo "Re-run with: CONFIRM=geobov bash deploy/aws/destroy.sh"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STATE_FILE="${ROOT_DIR}/deploy/aws/.provision-state.env"

if [[ ! -f "${STATE_FILE}" ]]; then
  echo "Missing ${STATE_FILE}. Nothing recorded to delete."
  exit 1
fi

# shellcheck disable=SC1090
source "${STATE_FILE}"
export AWS_DEFAULT_REGION="${AWS_REGION:-sa-east-1}"
export AWS_REGION="${AWS_DEFAULT_REGION}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }; }
need aws

if [[ -n "${ALLOCATION_ID:-}" && "${ALLOCATION_ID}" != "None" ]]; then
  echo "==> Releasing Elastic IP ${ALLOCATION_ID}"
  aws ec2 release-address --allocation-id "${ALLOCATION_ID}" || true
fi

if [[ -n "${INSTANCE_ID:-}" && "${INSTANCE_ID}" != "None" ]]; then
  echo "==> Terminating ${INSTANCE_ID}"
  aws ec2 terminate-instances --instance-ids "${INSTANCE_ID}" >/dev/null
  aws ec2 wait instance-terminated --instance-ids "${INSTANCE_ID}"
fi

if [[ -n "${SECURITY_GROUP_ID:-}" && "${SECURITY_GROUP_ID}" != "None" ]]; then
  echo "==> Deleting security group ${SECURITY_GROUP_ID}"
  aws ec2 delete-security-group --group-id "${SECURITY_GROUP_ID}" || true
fi

if [[ -n "${KEY_NAME:-}" ]]; then
  echo "==> Deleting key pair ${KEY_NAME} from AWS (local .pem is kept)"
  aws ec2 delete-key-pair --key-name "${KEY_NAME}" || true
fi

if [[ -n "${HOSTED_ZONE_ID:-}" ]]; then
  echo "Route 53 hosted zone ${HOSTED_ZONE_ID} was left in place."
  echo "Delete it in the console if you created one; a hosted zone is billed monthly."
fi

echo "GeoBov AWS resources from ${STATE_FILE} were removed."
echo "The free-plan account still exists until you close it or the trial ends."
