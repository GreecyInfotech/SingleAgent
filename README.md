# SingleAgent — Enterprise Agent Platform

Single agent design and development. Production-ready monorepo for enterprise AI agent orchestration.

## Monorepo Structure

```
enterprise-agent-platform/
├── agents/                    # Domain-specific AI agents
│   ├── customer-agent/
│   ├── loan-agent/
│   ├── fraud-agent/
│   ├── support-agent/
│   └── recommendation-agent/
├── orchestrator/              # LangGraph workflows & state
│   ├── langgraph/
│   ├── workflows/
│   └── state-management/
├── rag/                       # Retrieval-Augmented Generation
│   ├── embeddings/
│   ├── retrievers/
│   ├── vector-db/
│   └── chunking/
├── mcp-servers/               # Model Context Protocol integrations
│   ├── jira/ confluence/ github/
│   ├── salesforce/ sap/ oracle/ postgres/
├── tools/                     # Shared agent tools
│   ├── search/ email/ document-parser/ pdf/ reporting/
├── services/                  # Microservices
│   ├── auth-service/ user-service/ audit-service/
│   ├── notification-service/ gateway-service/
├── api-gateway/kong/          # Kong API gateway config
├── frontend/
│   ├── nextjs/                # Next.js dashboard
│   └── react/                 # React agent console
├── observability/
│   ├── prometheus/ grafana/ loki/ opentelemetry/
├── deployments/
│   ├── kubernetes/ helm/ terraform/
├── ci-cd/
│   ├── github-actions/ argo-cd/ sonar/
└── src/enterprise_agent_platform/  # Core API platform
```

## Documentation

- **[User Manual](usermanual.md)** — Complete end-to-end flows, API reference, deployment guide

## Quick Start

```bash
cp .env.example .env
pip install -e ".[dev]"
docker compose up -d db redis
make dev
```

- API Docs: http://localhost:8000/docs
- Next.js Dashboard: `cd frontend/nextjs && npm install && npm run dev`
- React Console: `cd frontend/react && npm install && npm run dev`
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Kong Gateway: http://localhost:8080

## Platform API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/platform/agents` | List domain agents |
| `POST /api/v1/platform/agents/{name}/execute` | Execute domain agent |
| `POST /api/v1/platform/orchestrate` | LangGraph intent routing |
| `GET /api/v1/platform/mcp-servers` | List MCP servers |
| `POST /api/v1/platform/mcp-servers/{server}/tools/{tool}` | Call MCP tool |

## Full Stack (Docker)

```bash
docker compose up -d --build
```

Services: API (8000), Auth (8001), Users (8002), Audit (8003), Notifications (8004), Gateway (8005), Kong (8080)

## Testing

```bash
make test
```

## Deployment

```bash
# Kubernetes
kubectl apply -f deployments/kubernetes/

# Helm
helm install eap deployments/helm/

# Terraform (Azure)
cd deployments/terraform && terraform init && terraform apply
```

## License

MIT
