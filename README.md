# production-ai-app

Production-ready starter project with:

- FastAPI backend (`app/`)
- Retrieval layer (`retrieval/`)
- Service orchestration (`services/`)
- Agent layer (`agents/`)
- Security guardrails (`security/`)
- Observability metrics (`observability/`)
- Test suite (`tests/`)
- Docker (`Dockerfile`, `docker-compose.yml`)
- Helm (`infra/helm/`)
- Terraform (`infra/terraform/`)
- CI pipeline (`.github/workflows/ci.yml`)

## Quick start

```bash
cd D:\personal\SingleAgent\production-ai-app
copy .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test

```bash
pytest -q
```

## Docker

```bash
docker compose up --build
```

## Documentation

- Architecture: `docs/architecture.md`
- User manual: `docs/user-manual.md`
- UML artifacts: `docs/uml-artifacts.md`
