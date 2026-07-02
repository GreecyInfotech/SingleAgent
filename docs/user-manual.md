# User Manual

## Purpose

`production-ai-app` is a production-oriented AI service template with:

- A FastAPI inference API
- A layered architecture for routing, planning, retrieval, and security
- Built-in observability and health endpoints
- Deployment assets for Docker, Helm, and Terraform

## Audience

- API consumers integrating chat capabilities
- Platform engineers deploying the service
- SRE/DevOps teams operating it in production
- Developers extending domain logic

## System Requirements

- Python 3.11+
- `pip` and virtual environment support
- Docker Desktop (optional, for container run)
- Kubernetes cluster + Helm (optional, for k8s deployment)
- Terraform CLI (optional, for infrastructure provisioning)

## Project Modules

- `app/`: API entrypoint, configuration, schemas
- `services/`: Query routing/orchestration logic
- `agents/`: Response planning logic
- `retrieval/`: Retrieval and grounding helpers
- `security/`: Input guardrails and safety checks
- `observability/`: Prometheus metric definitions and hooks
- `tests/`: API and integration test coverage
- `infra/`: Helm and Terraform deployment assets
- `docs/`: architecture and UML documentation

## Quick Start (Local)

1. Create environment:
   - `copy .env.example .env`
2. Create and activate virtual env:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
3. Install dependencies:
   - `pip install -e ".[dev]"`
4. Run API:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## Core API Endpoints

- `GET /health`: service liveness
- `GET /ready`: readiness probe
- `GET /metrics`: Prometheus metrics
- `POST /api/v1/chat`: main chat endpoint

### Chat Request Example

```json
{
  "message": "Summarize deployment steps",
  "session_id": "session-123"
}
```

### Chat Response Example

```json
{
  "answer": "Use Docker for local verification, then Helm for cluster rollout.",
  "confidence": 0.91,
  "route": "general"
}
```

## Running Tests

- `pytest -q`

Recommended for release gates:

- Unit and API tests
- Security scan/dependency checks
- Container build validation

## Running with Docker

- Build and start:
  - `docker compose up --build`
- Service URL:
  - `http://localhost:8000`

## Kubernetes Deployment (Helm)

- Chart path: `infra/helm`
- Validate:
  - `helm lint infra/helm`
- Render:
  - `helm template production-ai-app infra/helm`
- Install/upgrade:
  - `helm upgrade --install production-ai-app infra/helm`

## Infrastructure Provisioning (Terraform)

- Terraform root: `infra/terraform`
- Standard flow:
  - `terraform init`
  - `terraform plan`
  - `terraform apply`

## Production Operations

### Health and Readiness

- Liveness is served by `/health`
- Readiness is served by `/ready`
- Configure probes in your platform against these endpoints

### Observability

- Scrape `/metrics` for request count and latency
- Correlate API behavior with structured logs

### Security Controls

- Request content passes through `security/input_guard.py`
- Unsafe payloads are blocked with HTTP 400

### Error Handling

- Validation errors return standard FastAPI 4xx responses
- Unsafe input returns a deterministic blocked response

## Troubleshooting

- **App does not start**
  - Verify virtualenv is active and dependencies are installed
- **`/api/v1/chat` returns 400**
  - Check whether request input triggers safety guardrails
- **No metrics available**
  - Verify `/metrics` endpoint and Prometheus scrape target config
- **Container fails to run**
  - Rebuild image and verify `docker-compose.yml` configuration

## Release Checklist

- All tests pass
- Dependency vulnerabilities reviewed
- Environment variables validated
- Health/readiness/metrics endpoints verified
- Rollback plan documented

## Related Documents

- `docs/architecture.md`
- `docs/uml-artifacts.md`
