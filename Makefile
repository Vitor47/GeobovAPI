.PHONY: help install install-dev run test test-unit test-integration test-component \
        setup seed lint format clean docker-up docker-dev docker-down docker-logs \
        docker-ps docker-setup docker-seed docker-down-v pre-commit-install \
        aws-provision aws-validate aws-update aws-destroy

UV ?= uv
PYTHON = $(UV) run python

help: ## Show available commands
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies with uv
	$(UV) sync --frozen --no-dev

install-dev: ## Install production and development dependencies with uv
	$(UV) sync --frozen

run: ## Run API locally with hot reload
	$(UV) run uvicorn app.main:app --host 0.0.0.0 --port $${APP_PORT:-8000} --reload

test: ## Run all tests
	$(UV) run pytest tests/ -v

test-unit: ## Run unit tests only
	$(UV) run pytest tests/ -m unit -v

test-integration: ## Run integration tests only
	$(UV) run pytest tests/ -m integration -v

test-component: ## Run component tests only
	$(UV) run pytest tests/ -m component -v

setup: ## Initialize database, roles, and superuser (local Python)
	$(PYTHON) -m app.commands setup

seed: ## Seed idempotent dev sample data (local Python)
	$(PYTHON) -m app.commands seed

docker-up: ## Start production-like Docker stack (Postgres + Redis + Mongo + API)
	docker compose up -d --build

docker-dev: ## Start dev stack with hot reload and volume mount
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

docker-down: ## Stop Docker Compose services
	docker compose down

docker-down-v: ## Stop Docker Compose and remove volumes
	docker compose down -v

docker-logs: ## Follow API container logs
	docker compose logs -f api

docker-ps: ## Show running containers
	docker compose ps

docker-setup: ## Run DB setup inside the API container
	docker compose exec api python -m app.commands setup

docker-seed: ## Seed idempotent dev sample data inside Docker
	docker compose exec api python -m app.commands seed

docker-downsample: ## Run telemetry downsampling cron job inside Docker
	docker compose exec api python -m app.commands downsample-telemetry

pre-commit-install: ## Install pre-commit hooks
	$(UV) run pre-commit install

PYTHON_FILES := $(shell git ls-files --exclude-standard --cached --others | grep -E '\.py$$')

ifdef subdirectory
PYTHON_FILES := $(shell git ls-files --exclude-standard --cached --others $(subdirectory) | grep -E '\.py$$')
endif

lint-isort: ## Check import order with isort
	@echo "Linting isort..."
	-@$(UV) run isort --profile=black --line-length=88 --check-only --diff app tests alembic

lint-black: ## Check code formatting with black
	@echo "Linting black..."
	-@$(UV) run black --check --line-length=88 --preview app tests alembic

lint-flake8: ## Check style with flake8
	@echo "Linting flake8..."
	-@$(UV) run flake8 --statistics --exit-zero $(PYTHON_FILES)

lint-mypy: ## Run mypy type checker
	@echo "Linting mypy..."
	-@$(UV) run mypy $(PYTHON_FILES)

lint-pylint: ## Run pylint
	@echo "Linting pylint..."
	-@$(UV) run pylint --rcfile=.pylintrc $(PYTHON_FILES)

lint-flake8-critical: ## Check critical flake8 errors
	@echo "Linting flake8 criticals..."
	-@$(UV) run flake8 --statistics --exit-zero --select F401,F403,F405,F821,F823 $(PYTHON_FILES)

lint: lint-isort lint-black lint-flake8 lint-mypy lint-pylint lint-flake8-critical ## Run all linters

format-isort: ## Apply isort formatting
	@echo "Running isort..."
	$(UV) run isort --profile=black --line-length=88 app tests alembic

format-black: ## Apply black formatting
	@echo "Running black..."
	$(UV) run black --line-length=88 --preview app tests alembic

format-autoflake: ## Remove unused imports
	@echo "Running autoflake..."
	$(UV) run autoflake --in-place -vv --remove-all-unused-imports $(PYTHON_FILES)

format: format-autoflake format-isort format-black ## Apply all formatters

pre-commit-hook: ## Run pre-commit hook manually
	bash .git/hooks/pre-commit

clean: ## Remove __pycache__ and .pyc files
	@echo "Cleaning __pycache__ directories and .pyc files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Cleanup completed!"

aws-provision: ## Provision the GeoBov EC2 on the AWS free plan
	bash deploy/aws/provision.sh

aws-validate: ## Hit /health on the deployed GeoBov host
	bash deploy/aws/validate.sh

aws-update: ## Update GeoBov. Example: make aws-update ARGS="--api --migrate"
	bash deploy/aws/push-update.sh $(ARGS)

aws-destroy: ## Delete the GeoBov EC2 (requires CONFIRM=geobov)
	CONFIRM=$${CONFIRM:-} bash deploy/aws/destroy.sh
