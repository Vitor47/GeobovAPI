# AWS TCC deploy — CowTrack API

Low-cost single-EC2 deployment for the graduation project.

## What gets created

- EC2 `t3.micro` (Ubuntu 24.04) in `sa-east-1`
- Security group (SSH from your IP, HTTP/HTTPS open)
- Elastic IP
- Optional Route 53 domain registration for `apigeobov.com`
- Docker Compose: API + Postgres + Redis + Mongo
- Nginx + Let's Encrypt HTTPS

## One-time: AWS CLI credentials

You are logged into the AWS **console**, but this machine has **no API credentials** yet.

### Option A — Access keys (simplest)

1. AWS Console → **IAM** → Users → your user (or create `cowtrack-deploy`)
2. **Security credentials** → **Create access key** → CLI
3. In WSL run:

```bash
export PATH="$HOME/.local/bin:$PATH"
aws configure
# Access Key ID / Secret Access Key
# Default region: sa-east-1
# Output: json
```

### Option B — Console login session

```bash
export PATH="$HOME/.local/bin:$PATH"
aws configure set region sa-east-1
aws login
```

## Deploy

```bash
cd /home/vitor/house_agro/CowTrackAPI
export PATH="$HOME/.local/bin:$PATH"
export DOMAIN=apigeobov.com
export CERTBOT_EMAIL=seu-email@exemplo.com   # required for HTTPS

# Optional: buy the .com domain (~USD 12-15/year)
export REGISTER_DOMAIN=true
export CONTACT_FIRST_NAME=Vitor
export CONTACT_LAST_NAME=Sobrenome
export CONTACT_EMAIL=seu-email@exemplo.com
export CONTACT_PHONE=+55.11999999999
export CONTACT_ADDRESS='Rua Exemplo 123'
export CONTACT_CITY=Sao Paulo
export CONTACT_STATE=SP
export CONTACT_ZIP=01310100
export CONTACT_COUNTRY=BR

bash deploy/aws/provision.sh
bash deploy/aws/validate.sh
```

Without `REGISTER_DOMAIN=true`, the script still creates a Route 53 hosted zone and A record; you must point the registrar nameservers to Route 53 (or register the domain later).

## Files

| File | Purpose |
|------|---------|
| `provision.sh` | Creates AWS resources + uploads app + runs setup |
| `setup-server.sh` | Docker + Nginx + Certbot on the instance |
| `docker-compose.prod.yml` | Production stack (DB ports not public) |
| `.env.production.example` | Secrets template |
| `validate.sh` | Hits `/health` |
| `user-data.sh` | EC2 bootstrap (Docker install) |

Secrets (`deploy/aws/.env`, `*.pem`, `.provision-state.env`) are gitignored.
