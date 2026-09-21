#!/usr/bin/env bash
# Provision low-cost TCC infra in AWS (sa-east-1):
#   key pair, security group, EC2 t3.micro, Elastic IP, optional Route53 domain + DNS.
#
# Prerequisites:
#   - AWS CLI configured (aws configure OR aws login)
#   - python3, curl, rsync, ssh, openssl
#
# Usage:
#   export DOMAIN=apigeobov.com
#   export CERTBOT_EMAIL=you@email.com
#   export SSH_CIDR="$(curl -fsS https://checkip.amazonaws.com)/32"
#   # Optional domain registration (charges ~USD 12-15/year):
#   export REGISTER_DOMAIN=true
#   export CONTACT_FIRST_NAME=... CONTACT_LAST_NAME=... CONTACT_EMAIL=...
#   export CONTACT_PHONE=+55.11999999999 CONTACT_ADDRESS=... CONTACT_CITY=...
#   export CONTACT_STATE=SP CONTACT_ZIP=01310100 CONTACT_COUNTRY=BR
#   bash deploy/aws/provision.sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOY_DIR="${ROOT_DIR}/deploy/aws"
STATE_FILE="${DEPLOY_DIR}/.provision-state.env"

AWS_REGION="${AWS_REGION:-sa-east-1}"
DOMAIN="${DOMAIN:-apigeobov.com}"
KEY_NAME="${KEY_NAME:-cowtrack-tcc}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.micro}"
VOLUME_SIZE_GB="${VOLUME_SIZE_GB:-25}"
SG_NAME="${SG_NAME:-cowtrack-tcc-sg}"
INSTANCE_NAME="${INSTANCE_NAME:-cowtrack-tcc-api}"
REGISTER_DOMAIN="${REGISTER_DOMAIN:-false}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"

export AWS_DEFAULT_REGION="${AWS_REGION}"
export AWS_REGION

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1"; exit 1; }; }
need aws
need python3
need curl
need ssh
need scp
need rsync
need openssl


echo "==> Checking AWS identity..."
aws sts get-caller-identity >/dev/null
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
echo "Account: ${ACCOUNT_ID}  Region: ${AWS_REGION}"

if [[ -z "${SSH_CIDR:-}" ]]; then
  MY_IP="$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')"
  SSH_CIDR="${MY_IP}/32"
fi
echo "SSH allowed from: ${SSH_CIDR}"

KEY_FILE="${DEPLOY_DIR}/${KEY_NAME}.pem"
if ! aws ec2 describe-key-pairs --key-names "${KEY_NAME}" >/dev/null 2>&1; then
  echo "==> Creating key pair ${KEY_NAME}..."
  aws ec2 create-key-pair --key-name "${KEY_NAME}" --query 'KeyMaterial' --output text > "${KEY_FILE}"
  chmod 400 "${KEY_FILE}"
else
  echo "==> Key pair ${KEY_NAME} already exists."
  if [[ ! -f "${KEY_FILE}" ]]; then
    echo "WARNING: ${KEY_FILE} not found locally. You need the existing .pem to SSH."
  fi
fi

VPC_ID="$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)"
if [[ -z "${VPC_ID}" || "${VPC_ID}" == "None" ]]; then
  echo "No default VPC found. Create a default VPC in the console and re-run."
  exit 1
fi
SUBNET_ID="$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=${VPC_ID}" "Name=default-for-az,Values=true" \
  --query 'Subnets[0].SubnetId' --output text)"

SG_ID="$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=${SG_NAME}" "Name=vpc-id,Values=${VPC_ID}" \
  --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)"
if [[ -z "${SG_ID}" || "${SG_ID}" == "None" ]]; then
  echo "==> Creating security group ${SG_NAME}..."
  SG_ID="$(aws ec2 create-security-group \
    --group-name "${SG_NAME}" \
    --description "CowTrack TCC API (SSH + HTTP/HTTPS)" \
    --vpc-id "${VPC_ID}" \
    --query GroupId --output text)"
  aws ec2 authorize-security-group-ingress --group-id "${SG_ID}" \
    --ip-permissions \
    "IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=${SSH_CIDR},Description=SSH}]" \
    "IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTP}]" \
    "IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0,Description=HTTPS}]"
else
  echo "==> Using existing security group ${SG_ID}"
fi

AMI_ID="$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters \
    "Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*" \
    "Name=state,Values=available" \
  --query 'sort_by(Images,&CreationDate)[-1].ImageId' \
  --output text)"
if [[ -z "${AMI_ID}" || "${AMI_ID}" == "None" ]]; then
  AMI_ID="$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters \
      "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-noble-24.04-amd64-server-*" \
      "Name=state,Values=available" \
    --query 'sort_by(Images,&CreationDate)[-1].ImageId' \
    --output text)"
fi
echo "AMI: ${AMI_ID}"

INSTANCE_ID="$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=${INSTANCE_NAME}" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null || true)"

if [[ -z "${INSTANCE_ID}" || "${INSTANCE_ID}" == "None" ]]; then
  echo "==> Launching EC2 ${INSTANCE_TYPE}..."
  INSTANCE_ID="$(aws ec2 run-instances \
    --image-id "${AMI_ID}" \
    --instance-type "${INSTANCE_TYPE}" \
    --key-name "${KEY_NAME}" \
    --security-group-ids "${SG_ID}" \
    --subnet-id "${SUBNET_ID}" \
    --associate-public-ip-address \
    --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":${VOLUME_SIZE_GB},\"VolumeType\":\"gp3\",\"DeleteOnTermination\":true}}]" \
    --user-data "file://${DEPLOY_DIR}/user-data.sh" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${INSTANCE_NAME}},{Key=Project,Value=cowtrack-tcc}]" \
    --query 'Instances[0].InstanceId' --output text)"
  echo "Instance: ${INSTANCE_ID}"
  aws ec2 wait instance-running --instance-ids "${INSTANCE_ID}"
else
  echo "==> Reusing instance ${INSTANCE_ID}"
  aws ec2 start-instances --instance-ids "${INSTANCE_ID}" >/dev/null 2>&1 || true
  aws ec2 wait instance-running --instance-ids "${INSTANCE_ID}"
fi

ALLOC_ID="$(aws ec2 describe-addresses \
  --filters "Name=tag:Name,Values=${INSTANCE_NAME}" \
  --query 'Addresses[0].AllocationId' --output text 2>/dev/null || true)"
if [[ -z "${ALLOC_ID}" || "${ALLOC_ID}" == "None" ]]; then
  echo "==> Allocating Elastic IP..."
  ALLOC_ID="$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)"
  PUBLIC_IP="$(aws ec2 describe-addresses --allocation-ids "${ALLOC_ID}" --query 'Addresses[0].PublicIp' --output text)"
  aws ec2 create-tags --resources "${ALLOC_ID}" --tags "Key=Name,Value=${INSTANCE_NAME}"
else
  PUBLIC_IP="$(aws ec2 describe-addresses --allocation-ids "${ALLOC_ID}" --query 'Addresses[0].PublicIp' --output text)"
fi

ASSOC="$(aws ec2 describe-addresses --allocation-ids "${ALLOC_ID}" --query 'Addresses[0].InstanceId' --output text)"
if [[ "${ASSOC}" != "${INSTANCE_ID}" ]]; then
  echo "==> Associating Elastic IP ${PUBLIC_IP} -> ${INSTANCE_ID}"
  aws ec2 associate-address --instance-id "${INSTANCE_ID}" --allocation-id "${ALLOC_ID}" >/dev/null
fi

echo "==> Waiting for SSH on ${PUBLIC_IP}..."
for i in $(seq 1 60); do
  if ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -i "${KEY_FILE}" "ubuntu@${PUBLIC_IP}" "echo ok" 2>/dev/null; then
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "SSH timed out. Check security group and key file."
    exit 1
  fi
  sleep 5
done

# Wait for cloud-init / docker install
ssh -i "${KEY_FILE}" "ubuntu@${PUBLIC_IP}" 'bash -s' <<'REMOTE'
set -e
for i in $(seq 1 60); do
  if command -v docker >/dev/null 2>&1; then
    exit 0
  fi
  sleep 5
done
echo "Docker not installed yet"; exit 1
REMOTE

echo "==> Uploading application to /opt/cowtrack..."
ssh -i "${KEY_FILE}" "ubuntu@${PUBLIC_IP}" "sudo mkdir -p /opt/cowtrack && sudo chown ubuntu:ubuntu /opt/cowtrack"
rsync -az --delete \
  --exclude '.git' \
  --exclude 'venv' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.mypy_cache' \
  --exclude '.pytest_cache' \
  --exclude '.env' \
  -e "ssh -i ${KEY_FILE} -o StrictHostKeyChecking=accept-new" \
  "${ROOT_DIR}/" "ubuntu@${PUBLIC_IP}:/opt/cowtrack/"

if [[ ! -f "${DEPLOY_DIR}/.env" ]]; then
  echo "Creating ${DEPLOY_DIR}/.env from example with generated secrets..."
  SECRET_KEY="$(openssl rand -hex 32)"
  DB_PASS="$(openssl rand -hex 16)"
  ADMIN_PASS="$(openssl rand -hex 12)"
  sed \
    -e "s/CHANGE_ME_STRONG_PASSWORD/${DB_PASS}/" \
    -e "s/CHANGE_ME_LONG_RANDOM_SECRET/${SECRET_KEY}/" \
    -e "s/CHANGE_ME_ADMIN_PASSWORD/${ADMIN_PASS}/" \
    "${DEPLOY_DIR}/.env.production.example" > "${DEPLOY_DIR}/.env"
  echo "Generated admin password saved in deploy/aws/.env (keep it private)."
fi
scp -i "${KEY_FILE}" "${DEPLOY_DIR}/.env" "ubuntu@${PUBLIC_IP}:/opt/cowtrack/deploy/aws/.env"

HOSTED_ZONE_ID=""
if [[ "${REGISTER_DOMAIN}" == "true" ]]; then
  echo "==> Checking domain availability for ${DOMAIN}..."
  AVAIL="$(aws route53domains check-domain-availability --domain-name "${DOMAIN}" --region us-east-1 --query 'Availability' --output text)"
  echo "Availability: ${AVAIL}"
  if [[ "${AVAIL}" == "AVAILABLE" ]]; then
    for var in CONTACT_FIRST_NAME CONTACT_LAST_NAME CONTACT_EMAIL CONTACT_PHONE CONTACT_ADDRESS CONTACT_CITY CONTACT_STATE CONTACT_ZIP CONTACT_COUNTRY; do
      if [[ -z "${!var:-}" ]]; then
        echo "REGISTER_DOMAIN=true requires ${var}"
        exit 1
      fi
    done
    CONTACT_JSON="$(python3 - <<'PY'
import json, os
print(json.dumps({
  "FirstName": os.environ["CONTACT_FIRST_NAME"],
  "LastName": os.environ["CONTACT_LAST_NAME"],
  "ContactType": "PERSON",
  "AddressLine1": os.environ["CONTACT_ADDRESS"],
  "City": os.environ["CONTACT_CITY"],
  "State": os.environ["CONTACT_STATE"],
  "CountryCode": os.environ["CONTACT_COUNTRY"],
  "ZipCode": os.environ["CONTACT_ZIP"],
  "PhoneNumber": os.environ["CONTACT_PHONE"],
  "Email": os.environ["CONTACT_EMAIL"],
}))
PY
)"
    echo "==> Registering ${DOMAIN} (this incurs a yearly charge)..."
    OP_ID="$(aws route53domains register-domain \
      --region us-east-1 \
      --domain-name "${DOMAIN}" \
      --duration-in-years 1 \
      --auto-renew \
      --admin-contact "${CONTACT_JSON}" \
      --registrant-contact "${CONTACT_JSON}" \
      --tech-contact "${CONTACT_JSON}" \
      --query 'OperationId' --output text)"
    echo "Domain registration started. OperationId=${OP_ID}"
    echo "DNS may take minutes to hours to become usable."
  else
    echo "Domain not AVAILABLE (${AVAIL}). Will try existing hosted zone if present."
  fi
fi

HOSTED_ZONE_ID="$(aws route53 list-hosted-zones-by-name --dns-name "${DOMAIN}." \
  --query "HostedZones[?Name=='${DOMAIN}.'].Id" --output text | sed 's|/hostedzone/||' | head -n1 || true)"
if [[ -z "${HOSTED_ZONE_ID}" ]]; then
  echo "==> Creating hosted zone for ${DOMAIN}..."
  HOSTED_ZONE_ID="$(aws route53 create-hosted-zone \
    --name "${DOMAIN}" \
    --caller-reference "cowtrack-$(date +%s)" \
    --query 'HostedZone.Id' --output text | sed 's|/hostedzone/||')"
  echo "Hosted zone ${HOSTED_ZONE_ID} created."
  echo "If the domain was registered elsewhere, update its NS records to the Route53 nameservers."
  aws route53 get-hosted-zone --id "${HOSTED_ZONE_ID}" --query 'DelegationSet.NameServers' --output table
fi

echo "==> Upserting A record ${DOMAIN} -> ${PUBLIC_IP}"
CHANGE_BATCH="$(python3 - <<PY
import json
print(json.dumps({
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "${DOMAIN}.",
      "Type": "A",
      "TTL": 60,
      "ResourceRecords": [{"Value": "${PUBLIC_IP}"}],
    },
  }],
}))
PY
)"
aws route53 change-resource-record-sets \
  --hosted-zone-id "${HOSTED_ZONE_ID}" \
  --change-batch "${CHANGE_BATCH}" >/dev/null

echo "==> Running setup-server.sh on the instance..."
ssh -i "${KEY_FILE}" "ubuntu@${PUBLIC_IP}" \
  "sudo DOMAIN=${DOMAIN} CERTBOT_EMAIL=${CERTBOT_EMAIL} APP_DIR=/opt/cowtrack bash /opt/cowtrack/deploy/aws/setup-server.sh"

cat > "${STATE_FILE}" <<EOF
AWS_REGION=${AWS_REGION}
ACCOUNT_ID=${ACCOUNT_ID}
DOMAIN=${DOMAIN}
INSTANCE_ID=${INSTANCE_ID}
PUBLIC_IP=${PUBLIC_IP}
ALLOCATION_ID=${ALLOC_ID}
SECURITY_GROUP_ID=${SG_ID}
KEY_NAME=${KEY_NAME}
KEY_FILE=${KEY_FILE}
HOSTED_ZONE_ID=${HOSTED_ZONE_ID}
EOF

echo ""
echo "============================================"
echo "Provision complete"
echo "  Instance:  ${INSTANCE_ID}"
echo "  Public IP: ${PUBLIC_IP}"
echo "  Domain:    ${DOMAIN}"
echo "  SSH:       ssh -i ${KEY_FILE} ubuntu@${PUBLIC_IP}"
echo "  Health:    http://${DOMAIN}/health  (https after DNS+Certbot)"
echo "  State:     ${STATE_FILE}"
echo "============================================"
