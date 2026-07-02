.PHONY: install dev run test lint format migrate docker-up docker-down

install:
	pip install -e ".[dev]"

dev:
	uvicorn enterprise_agent_platform.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn enterprise_agent_platform.main:app --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=enterprise_agent_platform --cov-report=term-missing

lint:
	ruff check src tests
	mypy src

format:
	ruff check --fix src tests
	ruff format src tests

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f api
