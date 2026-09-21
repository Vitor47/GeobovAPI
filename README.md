# CowTrack API

API for cattle tracking built with **FastAPI**, **Clean Architecture**, **JWT authentication**, and **Redis session cache**.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Clone & Install](#clone--install)
- [Environment Variables](#environment-variables)
- [Run the Application](#run-the-application)
- [Docker](#docker)
- [Dev Data & CLI Commands](#dev-data--cli-commands)
- [Makefile](#makefile)
- [Tests](#tests)
- [Pre-commit](#pre-commit)
- [Project Structure](#project-structure)
- [API Overview](#api-overview)
- [Authentication & Permissions](#authentication--permissions)
- [Contributing](#contributing)

---

## Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.12+ |
| API Framework | FastAPI | 0.132.0 |
| ASGI Server | Uvicorn | 0.41.0 |
| ORM | SQLAlchemy | 2.0.46 |
| Migrations | Alembic | 1.18.4 |
| Validation | Pydantic | 2.12.5 |
| Database | PostgreSQL | 15 |
| Cache / Session | Redis | 7 |
| Auth | PyJWT | 2.13.0 |
| DI | dependency-injector | 4.48.3 |
| CLI | Click | 8.3.1 |
| API Docs | Scalar (scalar-fastapi) | 1.8.2 |
| Testing | pytest | 8.3.4 |

---

## Requirements

- **Python** 3.12 or higher
- **PostgreSQL** 15
- **Redis** 7
- **Git**
- *(optional)* **Docker** & **Docker Compose**
- *(optional)* **Make**

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Vitor47/CowTrackAPI.git
cd CowTrackAPI

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
make install-dev

# 4. Configure environment
cp .env.example .env

# 5. Start infrastructure (Postgres + Redis)
make docker-up

# 6. Initialize database + superuser + sample data
make seed

# 7. Run API
make run
```

Open **http://localhost:8000/docs/scalar** for the interactive API reference (Scalar).

---

## Clone & Install

### Clone the repository

```bash
git clone https://github.com/Vitor47/CowTrackAPI.git
cd CowTrackAPI
```

### Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### Install dependencies

**Production only:**

```bash
make install
# or
pip install -r requirements.txt
```

**Production + development (recommended for contributors):**

```bash
make install-dev
# or
pip install -r requirements.txt -r requirements-dev.txt
```

---

## Environment Variables

Copy the example file and adjust values:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST_PORT` | Host port for Docker Postgres | `5433` (avoids local 5432 conflict) |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/cow_track` |
| `SECRET_KEY` | JWT signing secret | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (minutes) | `1440` (24h) |
| `SESSION_CACHE_TTL_SECONDS` | Redis session TTL | `86400` (1 day) |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database index | `0` |
| `APP_PORT` | API port | `8000` |
| `SUPERUSER_EMAIL` | Dev superuser email | `admin@example.com` |
| `SUPERUSER_PASSWORD` | Dev superuser password | `changeme` |
| `SUPERUSER_FULL_NAME` | Dev superuser name | `Super Admin` |

> **Local without Docker:** set `DATABASE_URL=postgresql://postgres:postgres@localhost:5433/cow_track` and `REDIS_HOST=localhost` (use `5433` if Postgres runs via Docker).

---

## Run the Application

### With Make (recommended)

```bash
make run
```

### With Uvicorn directly

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### With Docker Compose (full stack)

Production-like stack (Postgres + Redis + API):

```bash
cp .env.example .env
make docker-up
```

Development stack with hot reload:

```bash
cp .env.example .env
make docker-dev
```

| Service | Container | Port | Notes |
|---------|-----------|------|-------|
| API | `cowtrack_api` | 8000 | `/health` checks DB + Redis |
| PostgreSQL | `cowtrack_postgres` | 5433 | persistent volume (host port) |
| Redis | `cowtrack_redis` | 6379 | AOF persistence, session cache |

Useful commands:

```bash
make docker-logs      # follow API logs
make docker-ps        # container status
make docker-setup     # run setup inside container
make docker-seed      # setup + sample data
make docker-down      # stop services
make docker-down-v    # stop and remove volumes
```

Stop services:

```bash
make docker-down
```

---

## Dev Data & CLI Commands

Management commands live under `app/commands/` and follow a Django-style workflow.

### Initial setup (tables + roles + superuser)

```bash
make setup
# or
python -m app.commands setup
# or
bash scripts/dev_setup.sh
```

### Seed sample dev data (company + farmer + cattle)

```bash
make seed
```

### Manual data insertion

**Create a company (farm):**

```bash
python -m app.commands create-company --name "Fazenda São João"
```

**Create a farmer (user linked to a company):**

```bash
python -m app.commands create-farmer \
  --full-name "João Silva" \
  --email "joao@fazenda.com" \
  --password "secret123" \
  --birth-date 1990-05-15 \
  --company-id 1 \
  --role manager
```

Available roles: `admin`, `manager`, `viewer`.

**Register a cattle animal:**

```bash
python -m app.commands create-cattle --tag TAG-001 --company-id 1
```

### Login as superuser

```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "changeme"}'
```

Use the returned `access_token` as `Authorization: Bearer <token>`.

---

## Makefile

Run `make help` to list all available commands:

```bash
make help
```

| Command | Description |
|---------|-------------|
| `make install` | Install production dependencies |
| `make install-dev` | Install prod + dev dependencies |
| `make run` | Start API with hot reload |
| `make setup` | Create tables, roles, and superuser |
| `make seed` | Setup + sample dev data |
| `make test` | Run all tests |
| `make test-unit` | Run unit tests |
| `make test-integration` | Run integration tests |
| `make test-component` | Run component tests |
| `make lint` | Run all linters |
| `make format` | Auto-format code |
| `make clean` | Remove `__pycache__` and `.pyc` files |
| `make docker-up` | Start production-like Docker stack |
| `make docker-dev` | Start dev stack with hot reload |
| `make docker-down` | Stop Docker Compose stack |
| `make docker-down-v` | Stop stack and remove volumes |
| `make docker-logs` | Follow API logs |
| `make docker-setup` | Run DB setup inside container |
| `make docker-seed` | Setup + sample dev data in Docker |
| `make pre-commit-install` | Install git pre-commit hooks |

Lint a specific folder:

```bash
make lint subdirectory=app/application
```

---

## Tests

Tests follow a layered structure under `tests/`:

```
tests/
├── user/       unit/ | integration/ | component/
├── company/    unit/ | integration/ | component/
└── cattle/     unit/ | integration/ | component/
```

```bash
make test                  # all tests
make test-unit             # unit only
make test-integration      # integration only
make test-component        # component only

pytest tests/cattle/unit/  # specific folder
pytest tests/ -m unit      # by marker
```

---

## Pre-commit

Install hooks to run linters automatically before each commit:

```bash
make pre-commit-install
# or
pre-commit install
```

Hooks configured in `.pre-commit-config.yaml`:

| Hook | Tool |
|------|------|
| Formatter | Black |
| Import order | isort |
| Linter | Flake8 |
| Type checker | mypy |
| Linter | Pylint |

Run hooks manually on all files:

```bash
pre-commit run --all-files
```

Run the hook script directly:

```bash
make pre-commit-hook
```

---

## Project Structure

```
CowTrackAPI/
├── app/
│   ├── adapters/          # Repositories, ORM models, DI container
│   ├── application/       # Use cases, steps, DTOs
│   ├── bootstrap/         # Routes, middleware, logging
│   ├── commands/          # CLI (setup, create-company, create-farmer…)
│   ├── core/              # Config, security, cache, permissions
│   ├── domain/            # Entities, repository contracts, enums
│   ├── presentation/      # FastAPI endpoints and schemas
│   └── main.py
├── alembic/               # Database migrations
├── scripts/               # Dev helper scripts
├── tests/                 # pytest test suite
├── .cursor/rules/         # Cursor AI project rules
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
└── requirements-dev.txt
```

Architecture flow:

```
Endpoint → UseCase.run() → Step._run() → Repository → ORM
```

---

## API Overview

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| `POST` | `/api/v1/users/login` | Public | Login and receive JWT |
| `POST` | `/api/v1/users/logout` | Bearer | Invalidate session cache |
| `GET` | `/api/v1/users/me` | Bearer | Current user info |
| `POST` | `/api/v1/users/` | Bearer | Create user |
| `GET` | `/api/v1/companies/{id}` | Bearer | Get company |
| `POST` | `/api/v1/cattle/` | Bearer | Create cattle telemetry |
| `GET` | `/api/v1/cattle/` | Bearer | List cattle data |
| `GET` | `/api/v1/cattle/{id}` | Bearer | Get cattle data by ID |
| `POST` | `/api/v1/devices/` | Bearer | Register LoRa collar (serial → cattle) |
| `GET` | `/api/v1/devices/` | Bearer | List devices |
| `GET` | `/api/v1/devices/{id}` | Bearer | Get device |
| `POST` | `/api/v1/gateways/` | Bearer | Register LoRa gateway (returns `api_key`) |
| `GET` | `/api/v1/gateways/` | Bearer | List gateways |
| `GET` | `/api/v1/gateways/{id}` | Bearer | Get gateway |
| `POST` | `/api/v1/gateways/ingest` | `X-Gateway-Api-Key` | Ingest GPS via gateway + `cow_id` |
| `GET` | `/health` | Public | DB + Redis health check |

### Interactive documentation

| URL | UI |
|-----|-----|
| http://localhost:8000/docs/scalar | **Scalar** (primary — modern, searchable) |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | OpenAPI 3 schema |

Documentation is powered by [Scalar](https://scalar.com) via `scalar-fastapi`, with JWT and gateway API key security schemes, request examples, and per-endpoint descriptions.

---

## Authentication & Permissions

- **JWT** carries `sub`, `email`, `company_id`, `role`, and `is_superuser`.
- **Redis** caches the session for **1 day** — no DB lookup on every request.
- **Superuser** bypasses role checks (like Django's `is_superuser`).
- Superusers must send `X-Company-Id: <id>` header to scope requests to a company.

**Roles:**

| Role | Description |
|------|-------------|
| `admin` | Full access within their company |
| `manager` | Can create cattle data |
| `viewer` | Read-only access |

---

## Contributing

1. **Fork** the repository and create a feature branch:

   ```bash
   git checkout -b feat/my-feature
   ```

2. **Install** dev dependencies and pre-commit:

   ```bash
   make install-dev
   make pre-commit-install
   ```

3. **Follow project conventions** (see `.cursor/rules/`):
   - Clean Architecture layers
   - English-only code and identifiers
   - Repository abstract documentation pattern
   - Tests in `tests/{app}/{unit,integration,component}/`

4. **Write tests** for new features:

   ```bash
   make test
   ```

5. **Lint and format** before committing:

   ```bash
   make format
   make lint
   ```

6. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):

   ```
   feat: add cattle export endpoint
   fix: resolve session cache TTL
   chore: update dependencies
   ```

7. **Open a Merge Request** with a clear description and test plan.

---

## License

Private project — House Agro / CowTrack.
