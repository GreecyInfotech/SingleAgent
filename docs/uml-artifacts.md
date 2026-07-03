# End-to-End UML Artifacts

This document provides an end-to-end architecture UML set for `production-ai-app` and aligned enterprise folders.

## 1) System Context Diagram

```mermaid
flowchart LR
    User[Enterprise User / Client App]
    FE[Frontend Next.js/React]
    Gateway[Kong API Gateway]
    API[FastAPI Platform API]
    Orch[Orchestrator / LangGraph]
    Agents[Domain Agents]
    Rag[RAG Services]
    MCP[MCP Servers]
    DB[(Datastores)]
    Obs[Observability Stack]

    User --> FE --> Gateway --> API
    API --> Orch --> Agents
    Orch --> Rag
    Agents --> MCP
    Rag --> DB
    API --> DB
    API --> Obs
    Orch --> Obs
```

## 2) Component Diagram

```mermaid
flowchart TD
    subgraph API Layer
      A[app/main.py]
      B[app/schemas/chat.py]
      C[security/input_guard.py]
      D[services/router.py]
    end

    subgraph Intelligence Layer
      E[agents/planner.py]
      F[orchestrator]
      G[rag/retrievers]
    end

    subgraph Integration Layer
      H[mcp_servers/registry.py]
      I[mcp-servers/*/server.py]
    end

    subgraph Platform Layer
      J[observability]
      K[deployments + infra]
    end

    A --> B
    A --> C
    A --> D
    D --> E
    E --> F
    F --> G
    F --> H
    H --> I
    A --> J
    K --> A
```

## 3) Sequence Diagram (End-to-End Request)

```mermaid
sequenceDiagram
    actor U as User
    participant FE as Frontend
    participant GW as API Gateway
    participant API as FastAPI
    participant Guard as Input Guard
    participant Router as Service Router
    participant Orch as Orchestrator
    participant Rag as Retrieval Layer
    participant MCP as MCP Registry/Server
    participant Obs as Metrics/Logs

    U->>FE: Submit query
    FE->>GW: HTTPS request
    GW->>API: Forward /api/v1/chat
    API->>Guard: Validate input
    alt Unsafe input
        Guard-->>API: Reject
        API-->>FE: 400 blocked response
    else Safe input
        Guard-->>API: Safe
        API->>Router: route_query(message)
        Router->>Orch: Select workflow
        Orch->>Rag: Retrieve context
        Orch->>MCP: Optional enterprise tool call
        Rag-->>Orch: Context bundle
        MCP-->>Orch: Tool output
        Orch-->>API: Final answer + confidence
        API->>Obs: Emit latency/request metrics
        API-->>FE: 200 ChatResponse
    end
```

## 4) Deployment Diagram

```mermaid
flowchart TB
    subgraph Client Side
      C1[Browser/Client]
    end

    subgraph Cluster
      Ingress[Ingress / Kong]
      PodAPI[API Pods]
      PodOrch[Orchestrator Pods]
      PodMCP[MCP Server Pods]
      Prom[Prometheus]
      Graf[Grafana]
    end

    subgraph CI_CD
      GH[GitHub Actions]
      Helm[Helm]
      TF[Terraform]
    end

    C1 --> Ingress --> PodAPI
    PodAPI --> PodOrch
    PodOrch --> PodMCP
    PodAPI --> Prom
    PodOrch --> Prom
    Prom --> Graf
    GH --> Helm
    GH --> TF
    Helm --> PodAPI
    Helm --> PodOrch
    Helm --> PodMCP
```

## 5) Package/Folder Dependency View

```mermaid
flowchart LR
    APP[app]
    SERVICES[services]
    AGENTS[agents]
    ORCH[orchestrator]
    RAG[rag + retrieval]
    MCPH[mcp_servers]
    MCPI[mcp-servers]
    OBS[observability]
    SEC[security]
    DEP[deployments + infra]
    TEST[tests]

    APP --> SEC
    APP --> SERVICES
    SERVICES --> AGENTS
    AGENTS --> ORCH
    ORCH --> RAG
    ORCH --> MCPH --> MCPI
    APP --> OBS
    DEP --> APP
    TEST --> APP
    TEST --> ORCH
```
