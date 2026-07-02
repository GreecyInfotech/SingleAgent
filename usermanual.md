# Enterprise Agent Platform — User Manual

Complete end-to-end guide for installing, implementing, operating, and extending the Enterprise Agent Platform.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Repository Structure](#2-repository-structure)
3. [Clean Architecture (`src/`)](#3-clean-architecture-src)
4. [Prerequisites](#4-prerequisites)
5. [End-to-End Implementation Flow](#5-end-to-end-implementation-flow)
6. [Runtime Request Flow](#6-runtime-request-flow)
7. [Configuration](#7-configuration)
8. [Business Use-Case Flows](#8-business-use-case-flows)
9. [Domain Agents](#9-domain-agents)
10. [API Reference](#10-api-reference)
11. [Frontend Dashboards](#11-frontend-dashboards)
12. [MCP Integrations](#12-mcp-integrations)
13. [RAG Knowledge Base](#13-rag-knowledge-base)
14. [Microservices](#14-microservices)
15. [Deployment](#15-deployment)
16. [Observability](#16-observability)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Overview

The **Enterprise Agent Platform (EAP)** is a production-ready monorepo for orchestrating AI agents across enterprise domains.

| Capability | Location | Description |
|------------|----------|-------------|
| **Core API** | `src/enterprise_agent_platform/` | FastAPI, clean architecture, LLM conversations |
| **Domain Agents** | `agents/` | Customer, Loan, Fraud, Support, Recommendation |
| **Orchestrator** | `orchestrator/` | LangGraph intent routing and workflow state |
| **RAG** | `rag/` | Embeddings, chunking, vector search |
| **MCP Servers** | `mcp-servers/` | Jira, Confluence, GitHub, Salesforce, SAP, Oracle, Postgres |
| **Tools** | `tools/` | Search, Email, Document Parser, PDF, Reporting |
| **Microservices** | `services/` | Auth, Users, Audit, Notifications, Gateway |
| **Frontend** | `frontend/nextjs`, `frontend/react` | Dashboard and agent console |
| **Deployments** | `deployments/` | Kubernetes, Helm, Terraform |

---

## 2. Repository Structure

```
enterprise-agent-platform/
├── src/enterprise_agent_platform/   # Core API (clean architecture)
├── agents/                          # Domain-specific agents
│   ├── customer-agent/
│   ├── loan-agent/
│   ├── fraud-agent/
│   ├── support-agent/
│   └── recommendation-agent/
├── orchestrator/
│   ├── langgraph/                   # Intent routing graph
│   ├── workflows/                   # Workflow runner
│   └── state-management/            # Workflow state store
├── rag/
│   ├── embeddings/
│   ├── retrievers/
│   ├── vector-db/
│   └── chunking/
├── mcp-servers/                     # External system integrations
├── tools/                           # Shared agent tools
├── services/                        # Microservices
├── frontend/
│   ├── nextjs/                      # Main dashboard
│   └── react/                       # Lightweight console
├── api-gateway/kong/
├── observability/
├── deployments/
├── ci-cd/
├── tests/
├── usermanual.md
└── pyproject.toml
```

---

## 3. Clean Architecture (`src/`)

The core API follows layered clean architecture:

```
src/enterprise_agent_platform/
├── main.py                    # Application entry point & lifespan
├── api/                       # HTTP layer (thin controllers)
│   ├── deps.py                # Dependency injection
│   ├── exception_handlers.py  # Global error handling
│   └── v1/
│       ├── health.py          # Health, readiness, metrics
│       ├── router.py          # LLM agent & conversation routes
│       └── platform.py        # Domain agent & orchestration routes
├── application/               # Use cases
│   ├── dto/                   # Request/response schemas
│   └── services/
│       ├── agent_service.py
│       ├── conversation_service.py
│       └── platform_service.py
├── domain/                    # Business entities & contracts
│   ├── models/                # Agent, Conversation, Message, etc.
│   └── interfaces/            # Repository & executor abstractions
├── core/                      # Cross-cutting concerns
│   ├── config.py
│   ├── logging.py
│   └── exceptions.py
└── infrastructure/            # External implementations
    ├── agents/                # LLM executor, tool registry
    └── persistence/           # SQLAlchemy ORM & repositories
```

### Layer responsibilities

| Layer | Responsibility | Example |
|-------|----------------|---------|
| **API** | HTTP routing, auth, validation | `platform.py` calls `PlatformService` |
| **Application** | Business orchestration | `PlatformService.execute_domain_agent()` |
| **Domain** | Entities and interfaces | `Agent`, `AgentRepository` |
| **Infrastructure** | DB, LLM, tools | `LLMAgentExecutor`, `SQLAgentRepository` |
| **Monorepo modules** | Domain agents, RAG, MCP | `agents/`, `rag/`, `mcp-servers/` |

---

## 4. Prerequisites

| Component | Version | Required |
|-----------|---------|----------|
| Python | 3.11+ | Yes |
| Node.js | 18+ | For frontend |
| pip | Latest | Yes |
| Docker & Docker Compose | Latest | Optional (PostgreSQL/Redis) |
| PostgreSQL | 16+ | Optional (SQLite works for dev) |
| OpenAI API Key | — | Optional (mock mode if empty) |

---

## 5. End-to-End Implementation Flow

This section walks through the **complete implementation journey** from a fresh clone to a running, testable platform.

### Phase 1 — Environment setup

```powershell
# 1. Navigate to project
cd enterprise-agent-platform

# 2. Create environment file
cp .env.example .env
```

Edit `.env` with minimum values:

```env
APP_ENV=development
SECRET_KEY=dev-secret-key-for-local-development-only-32chars
DATABASE_URL=sqlite+aiosqlite:///./enterprise_agents.db
OPENAI_API_KEY=sk-your-key-here
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8888"]
```

> **Note:** Use PostgreSQL for production. SQLite is fine for local development.
> If port `8000` is blocked on Windows, use port `8888` (see Phase 3).

```powershell
# 3. Install Python dependencies
pip install -e ".[dev]"
```

**Verify:**

```powershell
pytest tests/ -q
# Expected: 29 passed
```

---

### Phase 2 — Database initialization

**Option A — SQLite (quickest for dev)**

Tables are created automatically on startup when `APP_ENV != production`.

**Option B — PostgreSQL (production-like)**

```powershell
docker compose up -d db redis
alembic upgrade head
```

Update `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_agents
```

---

### Phase 3 — Start the backend

```powershell
cd enterprise-agent-platform
$env:PYTHONPATH = "src;."
uvicorn enterprise_agent_platform.main:app --reload --host 127.0.0.1 --port 8888
```

**Verify backend:**

| Check | URL |
|-------|-----|
| Health | http://127.0.0.1:8888/api/v1/health |
| API Docs | http://127.0.0.1:8888/docs |
| Metrics | http://127.0.0.1:8888/api/v1/metrics |
| Domain agents | http://127.0.0.1:8888/api/v1/platform/agents |

Expected health response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "database": "healthy",
  "redis": "unhealthy"
}
```

> Redis `unhealthy` is expected without `docker compose up redis`.

---

### Phase 4 — Start the frontend

**Next.js Dashboard (recommended):**

```powershell
cd frontend/nextjs
npm install
$env:NEXT_PUBLIC_API_URL = "http://localhost:8888"
npm run dev
```

Open: **http://localhost:3000** (or `3001` if `3000` is in use)

**React Console (alternative):**

```powershell
cd frontend/react
npm install
$env:VITE_API_URL = "http://localhost:8888"
npm run dev
```

Open: **http://localhost:3001**

---

### Phase 5 — Execute your first agent flow

#### 5.1 Via Frontend

1. Open the Next.js dashboard
2. Confirm **API Status: healthy**
3. Select **Customer Agent** from the dropdown
4. Enter query: `What segment is customer ACC-001 in?`
5. Click **Execute Agent** or **Auto-Route**

#### 5.2 Via API (curl)

```bash
# List all domain agents
curl http://127.0.0.1:8888/api/v1/platform/agents

# Execute customer agent directly
curl -X POST http://127.0.0.1:8888/api/v1/platform/agents/customer-agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "ACC-001",
    "query": "What segment is this customer in?"
  }'

# Auto-route via LangGraph orchestrator
curl -X POST http://127.0.0.1:8888/api/v1/platform/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Suspicious fraud alert on transaction TXN-99887",
    "context": {
      "transaction_id": "TXN-99887",
      "signals": ["unusual_amount", "geo_mismatch"]
    }
  }'
```

#### 5.3 Via LLM conversational agent

```bash
# Step 1: Create an LLM agent
curl -X POST http://127.0.0.1:8888/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Enterprise Assistant",
    "system_prompt": "You are a helpful enterprise assistant.",
    "tools": ["get_current_time", "search_knowledge", "calculate"]
  }'

# Step 2: Start a conversation (use agent id from step 1)
curl -X POST http://127.0.0.1:8888/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "<agent-uuid>", "title": "Help Session"}'

# Step 3: Send a message (use conversation id from step 2)
curl -X POST http://127.0.0.1:8888/api/v1/conversations/<conv-uuid>/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What time is it UTC? Calculate 15% of 8500."}'
```

---

### Phase 6 — Index knowledge (RAG)

Before agents return meaningful RAG results, index documents:

```python
import asyncio
from rag.embeddings.provider import OpenAIEmbeddingProvider
from rag.retrievers.hybrid import HybridRetriever
from rag.vector_db.client import VectorDBClient

async def index():
    provider = OpenAIEmbeddingProvider(api_key="sk-your-key")
    db = VectorDBClient("enterprise-kb")
    retriever = HybridRetriever(provider, db, score_threshold=0.0)

    await retriever.index_documents(
        texts=[
            "Loan policy: maximum DTI is 43%",
            "Fraud policy: block transactions above 0.9 risk score",
            "Customer segment: enterprise accounts above $1M ARR",
        ],
        metadata=[
            {"collection": "lending_policies"},
            {"collection": "fraud_policies"},
            {"collection": "customer_policies"},
        ],
    )
    print("Indexed 3 documents")

asyncio.run(index())
```

---

### Phase 7 — Full stack with Docker

```powershell
$env:OPENAI_API_KEY = "sk-your-key"
$env:SECRET_KEY = "your-production-secret-key-min-32-chars"
docker compose up -d --build
```

This starts: API, Auth, Users, Audit, Notifications, Gateway, Kong, PostgreSQL, Redis, Prometheus, Grafana, Loki.

---

### Phase 8 — Production deployment

```bash
# Kubernetes
kubectl apply -f deployments/kubernetes/

# Helm
helm install eap deployments/helm/ \
  --set secrets.openaiApiKey=sk-your-key \
  --set secrets.secretKey=your-32-char-secret

# Terraform (Azure AKS + PostgreSQL)
cd deployments/terraform && terraform init && terraform apply

# GitOps
kubectl apply -f ci-cd/argo-cd/application.yaml
```

---

### Implementation flow summary

```mermaid
flowchart TD
    A[Clone Repository] --> B[Create .env]
    B --> C[pip install -e .dev]
    C --> D{Database?}
    D -->|Dev| E[SQLite auto-create]
    D -->|Prod| F[docker compose db + alembic]
    E --> G[Start Backend :8888]
    F --> G
    G --> H[Verify /api/v1/health]
    H --> I[Start Frontend :3000]
    I --> J[Execute Domain Agent]
    J --> K{Need knowledge?}
    K -->|Yes| L[Index RAG documents]
    K -->|No| M[Use Orchestrator / LLM Chat]
    L --> M
    M --> N[Deploy with Docker/K8s/Helm]
```

---

## 6. Runtime Request Flow

### 6.1 Domain agent execution (direct)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as api/v1/platform.py
    participant Svc as PlatformService
    participant Agent as agents/customer-agent
    participant MCP as mcp-servers/salesforce
    participant RAG as rag/retrievers
    participant Tools as tools/search

    User->>Frontend: Enter query
    Frontend->>API: POST /platform/agents/customer-agent/execute
    API->>Svc: execute_domain_agent()
    Svc->>Agent: process(input_data)
    Agent->>MCP: invoke_mcp(get_account)
    Agent->>RAG: search_knowledge(query)
    Agent->>Tools: search(query)
    Agent-->>Svc: response + confidence + actions
    Svc-->>API: dict result
    API-->>Frontend: JSON response
    Frontend-->>User: Display result
```

**Code path:**

```
HTTP Request
  → api/v1/platform.py          (thin controller)
  → application/services/platform_service.py
  → agents/customer-agent/agent.py
  → agents/shared/services.py   (MCP, RAG, tools bridge)
  → mcp-servers/ | rag/ | tools/
  → JSON Response
```

---

### 6.2 Auto-routing (orchestrator)

```mermaid
sequenceDiagram
    participant User
    participant API as api/v1/platform.py
    participant Svc as PlatformService
    participant Runner as WorkflowRunner
    participant Graph as LangGraph
    participant Store as state-management
    participant Agent as Domain Agent

    User->>API: POST /platform/orchestrate
    API->>Svc: orchestrate(message, context)
    Svc->>Runner: run(message, context)
    Runner->>Store: create workflow state
    Runner->>Graph: ainvoke(initial_state)
    Graph->>Graph: route_intent (keyword match)
    Graph->>Agent: execute_agent()
    Agent-->>Graph: result
    Graph-->>Runner: final_state
    Runner->>Store: complete(workflow_id, result)
    Runner-->>Svc: workflow_id + agent + result
    Svc-->>API: response
    API-->>User: JSON with workflow_id
```

**Intent routing keywords:**

| Keywords in message | Routed agent |
|---------------------|--------------|
| loan, credit | `loan-agent` |
| fraud, suspicious | `fraud-agent` |
| support, ticket | `support-agent` |
| recommend, suggest | `recommendation-agent` |
| (default) | `customer-agent` |

**Check workflow state:**

```bash
curl http://127.0.0.1:8888/api/v1/platform/workflows/{workflow_id}
```

---

### 6.3 LLM conversational flow

```mermaid
sequenceDiagram
    participant User
    participant API as api/v1/router.py
    participant ConvSvc as ConversationService
    participant Executor as LLMAgentExecutor
    participant OpenAI
    participant Tools as tool_registry

    User->>API: POST /conversations/{id}/messages
    API->>ConvSvc: send_message()
    ConvSvc->>ConvSvc: save user message to DB
    ConvSvc->>Executor: execute(agent, history, input)
    Executor->>OpenAI: chat.completions.create()
    OpenAI-->>Executor: tool_calls (optional)
    Executor->>Tools: execute(tool_name, args)
    Tools-->>Executor: tool result
    Executor->>OpenAI: follow-up with tool results
    OpenAI-->>Executor: final assistant message
    Executor-->>ConvSvc: AgentExecutionResult
    ConvSvc->>ConvSvc: save assistant message to DB
    ConvSvc-->>API: ChatResponse
    API-->>User: user + assistant messages
```

---

## 7. Configuration

### Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | API key / JWT secret (min 32 chars) |
| `DATABASE_URL` | Yes | — | Async DB URL (SQLite or PostgreSQL) |
| `OPENAI_API_KEY` | No | — | OpenAI key (mock embeddings if empty) |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Default LLM model |
| `APP_ENV` | No | `development` | `development` / `production` / `testing` |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis cache |
| `CORS_ORIGINS` | No | localhost origins | Frontend allowed origins |
| `PORT` | No | `8000` | API server port |

### Per-agent configuration (`agents/*/config.yaml`)

```yaml
name: customer-agent
version: "1.0.0"
domain: customer
model: gpt-4o-mini
temperature: 0.5
tools:
  - search
  - get_customer_profile
mcp_servers:
  - salesforce
  - postgres
rag:
  enabled: true
  collections:
    - customer_policies
```

Loaded at runtime via `agents/shared/config_loader.py` and merged with code defaults.

---

## 8. Business Use-Case Flows

### Flow 1 — Customer inquiry

```bash
curl -X POST http://127.0.0.1:8888/api/v1/platform/agents/customer-agent/execute \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "ACC-001", "query": "What segment is this customer in?"}'
```

**Internal steps:** classify intent → Salesforce MCP → RAG search → enterprise search → response

**Sample response:**

```json
{
  "agent": "customer-agent",
  "response": "Customer ACC-001: intent=segmentation. Profile: Acme Corp. KB hits: 0. Search hits: 5.",
  "confidence": 0.92,
  "actions": ["classify_intent", "fetch_salesforce_account", "rag_search", "enterprise_search"],
  "intent": "segmentation"
}
```

---

### Flow 2 — Loan application

```bash
curl -X POST http://127.0.0.1:8888/api/v1/platform/agents/loan-agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "LOAN-2024-001",
    "customer_id": "CUST-100",
    "amount": 75000,
    "annual_income": 120000,
    "monthly_debt": 2500
  }'
```

**Internal steps:** DTI calculation → risk scoring → RAG policy lookup → Oracle MCP → decision (`pre_approved` or `manual_review`)

---

### Flow 3 — Fraud alert (auto-route)

```bash
curl -X POST http://127.0.0.1:8888/api/v1/platform/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Suspicious transaction detected",
    "context": {
      "transaction_id": "TXN-99887",
      "signals": ["unusual_amount", "geo_mismatch"]
    }
  }'
```

**Internal steps:** LangGraph routes to `fraud-agent` → signal scoring → report generation → workflow state saved

---

### Flow 4 — Support ticket

```bash
curl -X POST http://127.0.0.1:8888/api/v1/platform/agents/support-agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TKT-500",
    "query": "Application throws 500 error on login",
    "priority": "high"
  }'
```

**Internal steps:** RAG KB search → classify resolution → Jira MCP (if bug) → email (if password reset) → escalate if confidence < 0.6

---

### Flow 5 — MCP direct invocation

```bash
curl http://127.0.0.1:8888/api/v1/platform/mcp-servers

curl -X POST http://127.0.0.1:8888/api/v1/platform/mcp-servers/jira/tools/create_issue \
  -H "Content-Type: application/json" \
  -d '{
    "arguments": {
      "project": "EAP",
      "summary": "Deploy agent platform to production"
    }
  }'
```

---

## 9. Domain Agents

| Agent | Folder | MCP Servers | RAG | Primary actions |
|-------|--------|-------------|-----|-----------------|
| `customer-agent` | `agents/customer-agent/` | Salesforce, Postgres | Yes | Profile lookup, segmentation |
| `loan-agent` | `agents/loan-agent/` | Oracle, Postgres, SAP | Yes | DTI calc, risk scoring |
| `fraud-agent` | `agents/fraud-agent/` | Postgres, Oracle | No | Signal scoring, reporting |
| `support-agent` | `agents/support-agent/` | Jira, Confluence, GitHub | Yes | KB search, ticket creation |
| `recommendation-agent` | `agents/recommendation-agent/` | Salesforce, Postgres | Yes | Product recommendations |

Each agent extends `agents/shared/base.py` → `BaseEnterpriseAgent` and uses `agents/shared/services.py` for MCP, RAG, and tool access.

---

## 10. API Reference

### Health & monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check with DB/Redis status |
| GET | `/api/v1/live` | Kubernetes liveness probe |
| GET | `/api/v1/ready` | Kubernetes readiness probe |
| GET | `/api/v1/metrics` | Prometheus metrics |

### Platform (domain agents)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/platform/agents` | List all domain agents |
| GET | `/api/v1/platform/agents/{name}` | Get agent configuration |
| POST | `/api/v1/platform/agents/{name}/execute` | Execute domain agent |
| POST | `/api/v1/platform/orchestrate` | Auto-route via LangGraph |
| GET | `/api/v1/platform/workflows/{id}` | Get workflow state |
| GET | `/api/v1/platform/mcp-servers` | List MCP servers and tools |
| POST | `/api/v1/platform/mcp-servers/{server}/tools/{tool}` | Invoke MCP tool |

### Core (LLM agents)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents` | Create LLM agent |
| GET | `/api/v1/agents` | List agents |
| GET | `/api/v1/agents/{id}` | Get agent |
| PATCH | `/api/v1/agents/{id}` | Update agent |
| DELETE | `/api/v1/agents/{id}` | Delete agent |
| POST | `/api/v1/conversations` | Start conversation |
| POST | `/api/v1/conversations/{id}/messages` | Send message (LLM + tools) |
| GET | `/api/v1/conversations/{id}/messages` | Get message history |
| GET | `/api/v1/tools` | List registered tools (8 tools) |

### Authentication

In production (`APP_ENV=production`), include:

```
X-Api-Key: <your-SECRET_KEY-value>
```

---

## 11. Frontend Dashboards

### Next.js (`frontend/nextjs`)

| Feature | Description |
|---------|-------------|
| Agent dropdown | Select any of 5 domain agents |
| Execute Agent | Direct call to `/platform/agents/{name}/execute` |
| Auto-Route | Calls `/platform/orchestrate` |
| Health indicator | Live status from `/api/v1/health` |

```powershell
$env:NEXT_PUBLIC_API_URL = "http://localhost:8888"
npm run dev
```

### React (`frontend/react`)

Lightweight console with the same execute and orchestrate capabilities.

```powershell
$env:VITE_API_URL = "http://localhost:8888"
npm run dev
```

---

## 12. MCP Integrations

| Server | Tools | Used by |
|--------|-------|---------|
| **jira** | create_issue, get_issue, search_issues | support-agent |
| **confluence** | search_pages, get_page | support-agent |
| **github** | search_repos, get_pull_request, create_issue | support-agent |
| **salesforce** | query_soql, get_account, create_lead | customer-agent, recommendation-agent |
| **sap** | get_material, get_purchase_order | loan-agent |
| **oracle** | execute_query, get_customer | loan-agent, fraud-agent |
| **postgres** | query, list_tables | customer-agent, loan-agent, fraud-agent |

Python package: `mcp_servers/` (loads implementations from `mcp-servers/`).

---

## 13. RAG Knowledge Base

### Components

| Module | File | Purpose |
|--------|------|---------|
| Embeddings | `rag/embeddings/provider.py` | OpenAI embeddings (mock if no key) |
| Chunking | `rag/chunking/strategies.py` | Fixed-size and sentence chunking |
| Vector DB | `rag/vector-db/client.py` | In-memory vector store (swap for pgvector in prod) |
| Retriever | `rag/retrievers/hybrid.py` | Vector similarity search |

### Registered tools using RAG

- `search_knowledge` — in `tool_registry.py`, used by LLM agents
- `agents/shared/services.py` — used by domain agents with `rag_enabled: true`

---

## 14. Microservices

| Service | Port | Start command |
|---------|------|---------------|
| Core API | 8888 / 8000 | `uvicorn enterprise_agent_platform.main:app` |
| Auth | 8001 | `uvicorn main:app --app-dir services/auth-service` |
| Users | 8002 | `uvicorn main:app --app-dir services/user-service` |
| Audit | 8003 | `uvicorn main:app --app-dir services/audit-service` |
| Notifications | 8004 | `uvicorn main:app --app-dir services/notification-service` |
| Gateway | 8005 | `uvicorn main:app --app-dir services/gateway-service` |
| Kong | 8080 | `docker compose up kong` |

Or start all: `docker compose up -d --build`

---

## 15. Deployment

### Kubernetes

```bash
kubectl apply -f deployments/kubernetes/
```

### Helm

```bash
helm install eap deployments/helm/ \
  --set secrets.openaiApiKey=sk-your-key \
  --set secrets.secretKey=your-32-char-secret
```

Templates: `deployments/helm/templates/` (Deployment, Service, Ingress, Secret)

### Terraform (Azure)

```bash
cd deployments/terraform
terraform init && terraform apply
```

### Argo CD

```bash
kubectl apply -f ci-cd/argo-cd/application.yaml
```

---

## 16. Observability

| Tool | URL | Purpose |
|------|-----|---------|
| Prometheus | http://localhost:9090 | Metrics scraping |
| Grafana | http://localhost:3000 | Dashboards |
| Loki | http://localhost:3100 | Log aggregation |
| API Metrics | http://127.0.0.1:8888/api/v1/metrics | `eap_up`, `eap_uptime_seconds` |

---

## 17. Troubleshooting

### Port 8000 blocked (Windows)

```
ERROR: [WinError 10013] An attempt was made to access a socket...
```

**Fix:** Use port 8888:

```powershell
uvicorn enterprise_agent_platform.main:app --reload --host 127.0.0.1 --port 8888
```

Update frontend: `NEXT_PUBLIC_API_URL=http://localhost:8888`

### SQLite pool error

```
TypeError: Invalid argument(s) 'pool_size','max_overflow' sent to create_engine()
```

**Fix:** Already handled in `infrastructure/persistence/database.py` — SQLite URLs skip pool settings.

### API returns 404 on /health

**Fix:** Ensure `health.router` is included in `main.py` (it registers at `/api/v1/health`, not `/health`).

### Frontend shows API unreachable

1. Confirm backend is running: `curl http://127.0.0.1:8888/api/v1/health`
2. Set `NEXT_PUBLIC_API_URL` to match backend port
3. Add frontend origin to `CORS_ORIGINS` in `.env`

### Tests

```powershell
$env:APP_ENV = "testing"
$env:SECRET_KEY = "test-secret-key-at-least-32-chars-long"
$env:DATABASE_URL = "sqlite+aiosqlite:///:memory:"
pytest tests/ -v
```

### Production checklist

- [ ] `SECRET_KEY` — 32+ characters
- [ ] `OPENAI_API_KEY` configured
- [ ] PostgreSQL + `alembic upgrade head` (no auto `create_tables`)
- [ ] `APP_ENV=production` + `X-Api-Key` header enforced
- [ ] Kong gateway in front of API
- [ ] Prometheus scraping `/api/v1/metrics`
- [ ] MCP servers connected to real credentials
- [ ] RAG indexed with production documents

---

## Quick Reference

```powershell
# Setup
pip install -e ".[dev]"
cp .env.example .env

# Backend
$env:PYTHONPATH = "src;."
uvicorn enterprise_agent_platform.main:app --reload --host 127.0.0.1 --port 8888

# Frontend
cd frontend/nextjs
$env:NEXT_PUBLIC_API_URL = "http://localhost:8888"
npm run dev

# Health
curl http://127.0.0.1:8888/api/v1/health

# Execute agent
curl -X POST http://127.0.0.1:8888/api/v1/platform/agents/customer-agent/execute `
  -H "Content-Type: application/json" `
  -d '{"customer_id":"C001","query":"customer segment"}'

# Auto-route
curl -X POST http://127.0.0.1:8888/api/v1/platform/orchestrate `
  -H "Content-Type: application/json" `
  -d '{"message":"fraud alert on TXN-123"}'

# Tests
pytest tests/ -q
```

---

*Enterprise Agent Platform v1.0.0 — User Manual*
