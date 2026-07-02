# UML Artifacts

This document provides core UML views for `production-ai-app` using Mermaid.

## 1) Use Case Diagram

```mermaid
flowchart LR
    User[API Consumer]
    DevOps[DevOps/SRE]
    Platform[Kubernetes/Infra Admin]
    API[FastAPI Service]

    User -->|Submit chat prompt| API
    User -->|Read answer| API
    DevOps -->|Check health/ready| API
    DevOps -->|Monitor metrics| API
    Platform -->|Deploy service| API
```

## 2) Component Diagram

```mermaid
flowchart TD
    A[app/main.py<br/>FastAPI Endpoints]
    B[security/input_guard.py<br/>Input Safety]
    C[services/router.py<br/>Route Selection]
    D[retrieval/hybrid_search.py<br/>Context Retrieval]
    E[agents/planner.py<br/>Response Planning]
    F[app/schemas/chat.py<br/>API Contracts]
    G[observability/metrics/registry.py<br/>Prometheus Metrics]

    A --> F
    A --> B
    A --> C
    C --> D
    A --> E
    A --> G
```

## 3) Sequence Diagram (Chat Request)

```mermaid
sequenceDiagram
    actor Client as API Consumer
    participant API as FastAPI /api/v1/chat
    participant Guard as InputGuard
    participant Router as QueryRouter
    participant Retrieval as HybridSearch
    participant Planner as AgentPlanner

    Client->>API: POST /api/v1/chat {message, session_id}
    API->>Guard: is_safe_user_input(message)
    alt Unsafe input
        Guard-->>API: false
        API-->>Client: 400 Blocked unsafe input
    else Safe input
        Guard-->>API: true
        API->>Router: route_query(message)
        Router->>Retrieval: fetch context
        Retrieval-->>Router: context
        Router-->>API: route, context
        API->>Planner: plan_response(route, message, context)
        Planner-->>API: answer, confidence
        API-->>Client: 200 ChatResponse
    end
```

## 4) Deployment Diagram

```mermaid
flowchart TB
    subgraph ClientLayer
        U[Client Apps]
    end

    subgraph Runtime
        LB[Ingress / Load Balancer]
        POD[production-ai-app Pod]
        MET[Prometheus]
    end

    subgraph ConfigInfra
        HELM[Helm Chart]
        TF[Terraform]
        CI[GitHub Actions CI]
    end

    U --> LB --> POD
    POD -->|/metrics| MET
    CI --> HELM
    CI --> TF
    HELM --> POD
```

## 5) Package/Folder View

```mermaid
flowchart LR
    APP[app]
    SERVICES[services]
    AGENTS[agents]
    RETRIEVAL[retrieval]
    SECURITY[security]
    OBS[observability]
    INFRA[infra]
    TESTS[tests]
    DOCS[docs]

    APP --> SERVICES
    APP --> AGENTS
    APP --> SECURITY
    SERVICES --> RETRIEVAL
    APP --> OBS
    INFRA --> APP
    TESTS --> APP
    DOCS --> APP
```
