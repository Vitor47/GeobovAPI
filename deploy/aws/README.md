# GeoBov on AWS

One small EC2 runs the API, Postgres, Redis, and Mongo. GitHub Actions deploys it.

The default setup does **not** buy a domain and does **not** create Route 53, so those bills stay at zero.

## What you pay

AWS no longer gives a permanent free `t3.micro`. For an account created on or after 15 July 2025:

- Choose the **Free plan** at signup, not the Paid plan. The Free plan cannot charge your card. It ends after 6 months or when the credits run out, whichever comes first.
- New accounts receive **USD 100** in credits, and can earn up to **USD 100** more.
- GeoBov uses one `t4g.small` (2 GB RAM) and a 20 GB disk in `sa-east-1`. That draws down those credits. It is enough for a graduation project if you do not add databases, load balancers, or a domain.
- An AWS Academy / classroom lab is a poor fit: those accounts expire and often block a server that stays online.

Leave the instance running while you need the API. An Elastic IP costs credits when it is not attached to a running instance.

When the project is over:

```bash
CONFIRM=geobov bash deploy/aws/destroy.sh
```

## Pipelines

| Workflow | When it runs | What it does |
|----------|----------------|--------------|
| `GeoBov CI` | Pull request only | isort, black, flake8, mypy, pylint, pytest |
| `GeoBov deploy` | Tag `v*` | Uploads the code, rebuilds the API, runs migrations |
| `GeoBov deploy` | Actions → Run workflow | You pick the services and whether to migrate |

A tag such as `v1.0.0` updates the API and runs `alembic upgrade head`. It does not recreate Postgres, Redis, or Mongo.

To choose by hand: GitHub → **Actions** → **GeoBov deploy** → **Run workflow**.

| Checkbox | Effect |
|----------|--------|
| Rebuild and restart the API | New code, new container. Database volume stays. |
| Update Postgres / Redis / MongoDB | New image only. Volumes stay. |
| Run database migrations | `alembic upgrade head` inside the API image |

The same choices exist from your machine after the first provision:

```bash
bash deploy/aws/push-update.sh --api --migrate
bash deploy/aws/push-update.sh --postgres
bash deploy/aws/push-update.sh --all
```

## One-time server

1. Create an AWS account and pick the **Free** plan. Region later used by the script: `sa-east-1`.
2. IAM → your user → **Create access key** → CLI.
3. On this machine:

```bash
aws configure
# region: sa-east-1
# output: json
```

4. Create the server:

```bash
bash deploy/aws/provision.sh
```

The script prints the public IP and writes `deploy/aws/.provision-state.env`. Secrets are stored as one Standard `SecureString` at `/geobov/prod/env` and copied to `deploy/aws/.env` on the server with mode `600`. The admin password is in that file. Do not commit it.

HTTPS uses a free Let's Encrypt certificate. With no domain, it is an IP certificate (about 6 days, renewed by Certbot). Set `CERTBOT_EMAIL` before provisioning.

Health check:

```bash
bash deploy/aws/validate.sh
```

Open `https://<public-ip>/health`. Port 80 only answers the certificate challenge and redirects everything else to HTTPS.

## GitHub Actions secrets

Repository → **Settings** → **Secrets and variables** → **Actions**:

| Secret | Value |
|--------|--------|
| `GEBOV_SSH_HOST` | Public IP printed by `provision.sh` |
| `GEBOV_SSH_KEY` | Full contents of `deploy/aws/geobov.pem`, including the BEGIN and END lines |
| `GEBOV_SSH_USER` | Optional. Default is `ubuntu` |

Then:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Or run **GeoBov deploy** manually and tick the boxes you want.

GitHub-hosted minutes are free on public repositories. Private repositories include 2,000 minutes per month.

## Files

| File | Purpose |
|------|---------|
| `provision.sh` | Creates the EC2, Elastic IP, and the first deploy |
| `update.sh` | On the server: chosen services and optional migrations |
| `push-update.sh` | From your machine: upload code, then `update.sh` |
| `setup-server.sh` | Docker, Nginx, and the first `docker compose up` |
| `destroy.sh` | Deletes the instance, Elastic IP, and security group |
| `docker-compose.prod.yml` | API + Postgres + Redis + Mongo |
| `.env.production.example` | Secret template |

`CERTBOT_EMAIL` is required. Without `DOMAIN`, Let's Encrypt issues a free certificate for the public IP. It lasts about six days and Certbot renews it. Buying `apigeobov.com` or turning on Route 53 (`ENABLE_ROUTE53=true`) is optional and costs money. The script refuses to register a domain unless `CONFIRM_PAID_DOMAIN=true`.
