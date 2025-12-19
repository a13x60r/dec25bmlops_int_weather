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
