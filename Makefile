SHELL := /bin/bash

.PHONY: venv install precommit format lint test mlflow-up mlflow-down docker-build docker-run

venv:
	python -m venv .venv

install: venv
	source .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && pip install -e .

precommit:
	source .venv/bin/activate && pre-commit install

format:
	source .venv/bin/activate && ruff format .

lint:
	source .venv/bin/activate && ruff check .

test:
	source .venv/bin/activate && pytest

mlflow-up:
	docker compose up -d mlflow

mlflow-down:
	docker compose down

docker-build:
	docker build -t weather-au-mlops:dev .

docker-run:
	docker run --rm --env-file .env --network host weather-au-mlops:dev

help:
	@echo "Available commands:"
	@echo "  make venv           - Create python virtual environment"
	@echo "  make install        - Install dependencies"
	@echo "  make precommit      - Install pre-commit hooks"
	@echo "  make format         - Format code with ruff"
	@echo "  make lint           - Lint code with ruff"
	@echo "  make test           - Run tests with pytest"
	@echo "  make mlflow-up      - Start MLflow service"
	@echo "  make mlflow-down    - Stop MLflow service"
	@echo "  make docker-build   - Build Docker image for dev"
	@echo "  make docker-run     - Run Docker image for dev"
