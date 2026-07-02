# Architecture

`production-ai-app` follows a layered approach:

1. `app/` presentation & API contracts
2. `services/` orchestration and routing
3. `agents/` planning/decision logic
4. `retrieval/` context lookup
5. `security/` input guardrails
6. `observability/` metrics and tracing hooks

Deployments are provided through Docker, Helm, and Terraform.

## Folder-Wise Production Implementation

- `app/`
  - `main.py`: API entrypoint, middleware, health/ready/metrics/chat endpoints
  - `config.py`: central settings model
  - `schemas/chat.py`: request/response contracts for `/api/v1/chat`
- `services/`
  - `router.py`: routes incoming queries to correct downstream path
- `agents/`
  - `planner.py`: creates final answer from route + context
- `retrieval/`
  - `hybrid_search.py`: retrieval utility for contextual grounding
- `security/`
  - `input_guard.py`: validates and blocks unsafe user payloads
- `observability/`
  - `metrics/registry.py`: Prometheus counters/histograms
- `tests/`
  - `test_api.py`: health and API contract validation
- `infra/helm/`
  - chart, values, deployment and service templates
- `infra/terraform/`
  - base infrastructure provisioning entrypoint
- `.github/workflows/`
  - CI checks and automated validation

## Supporting Artifacts

- User operations and runbook: `docs/user-manual.md`
- UML package and behavior diagrams: `docs/uml-artifacts.md`
