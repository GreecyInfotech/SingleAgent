.PHONY: install dev api worker infra test

install:
	pip install -e ".[dev]"

dev: infra
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8100

api:
	uvicorn app.main:app --host 0.0.0.0 --port 8100

worker:
	python -m worker.main

infra:
	docker compose up -d zookeeper kafka minio

test:
	pytest -q
