.PHONY: help install install-dev run test test-unit test-integration test-component \
        setup seed lint format clean docker-up docker-dev docker-down docker-logs \
        docker-ps docker-setup docker-seed docker-down-v pre-commit-install

help: ## Show available commands
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install production + development dependencies
	pip install -r requirements.txt -r requirements-dev.txt

run: ## Run API locally with hot reload
	uvicorn app.main:app --host 0.0.0.0 --port $${APP_PORT:-8000} --reload

test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/ -m unit -v

test-integration: ## Run integration tests only
	pytest tests/ -m integration -v

test-component: ## Run component tests only
	pytest tests/ -m component -v

setup: ## Initialize database, roles, and superuser
	python -m app.commands setup

seed: setup ## Alias for setup + sample dev data
	python -m app.commands create-company --name "Dev Farm"
	python -m app.commands create-farmer \
		--full-name "Dev Farmer" \
		--email "farmer@dev.local" \
		--password "dev123456" \
		--birth-date 1990-01-01 \
		--company-id 1 \
		--role manager
	python -m app.commands create-cattle --tag DEV-001 --company-id 1

docker-up: ## Start production-like Docker stack (Postgres + Redis + API)
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

docker-seed: docker-setup ## Seed sample dev data inside Docker
	docker compose exec api python -m app.commands create-company --name "Dev Farm"
	docker compose exec api python -m app.commands create-farmer \
		--full-name "Dev Farmer" \
		--email "farmer@dev.local" \
		--password "dev123456" \
		--birth-date 1990-01-01 \
		--company-id 1 \
		--role manager
	docker compose exec api python -m app.commands create-cattle --tag DEV-001 --company-id 1

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

PYTHON_FILES := $(shell git ls-files --exclude-standard --cached --others | grep -E '\.py$$')

ifdef subdirectory
PYTHON_FILES := $(shell git ls-files --exclude-standard --cached --others $(subdirectory) | grep -E '\.py$$')
endif

lint-isort: ## Check import order with isort
	@echo "Linting isort..."
	-@isort --profile=black --line-length=88 --check-only --diff app tests alembic

lint-black: ## Check code formatting with black
	@echo "Linting black..."
	-@black --check --line-length=88 --preview app tests alembic

lint-flake8: ## Check style with flake8
	@echo "Linting flake8..."
	-@flake8 --statistics --exit-zero $(PYTHON_FILES)

lint-mypy: ## Run mypy type checker
	@echo "Linting mypy..."
	-@mypy $(PYTHON_FILES)

lint-pylint: ## Run pylint
	@echo "Linting pylint..."
	-@PYTHONPATH=$(shell pwd) pylint --rcfile=.pylintrc $(PYTHON_FILES)

lint-flake8-critical: ## Check critical flake8 errors
	@echo "Linting flake8 criticals..."
	-@flake8 --statistics --exit-zero --select F401,F403,F405,F821,F823 $(PYTHON_FILES)

lint: lint-isort lint-black lint-flake8 lint-mypy lint-pylint lint-flake8-critical ## Run all linters

format-isort: ## Apply isort formatting
	@echo "Running isort..."
	isort --profile=black --line-length=88 app tests alembic

format-black: ## Apply black formatting
	@echo "Running black..."
	black --line-length=88 --preview app tests alembic

format-autoflake: ## Remove unused imports
	@echo "Running autoflake..."
	autoflake --in-place -vv --remove-all-unused-imports $(PYTHON_FILES)

format: format-autoflake format-isort format-black ## Apply all formatters

pre-commit-hook: ## Run pre-commit hook manually
	bash .git/hooks/pre-commit

clean: ## Remove __pycache__ and .pyc files
	@echo "Cleaning __pycache__ directories and .pyc files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Cleanup completed!"
