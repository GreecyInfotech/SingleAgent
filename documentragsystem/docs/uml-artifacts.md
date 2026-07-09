# End-to-End UML Artifacts

This document provides a complete UML artifact set for the **Document RAG System** — from client upload through async ingestion, vector indexing, retry handling, and status polling.

---

## 1) System Context Diagram

High-level actors and external systems interacting with the pipeline.

```mermaid
flowchart LR
    Client[Client / curl / App]
    API[FastAPI Upload API]
    Kafka[(Kafka)]
    S3[(S3 / MinIO)]
    Worker[Ingestion Worker]
    Chroma[(Chroma Vector DB)]
    SQLite[(SQLite Idempotency DB)]
    DLQ[(DLQ Topic)]

    Client -->|POST upload / GET status| API
    API -->|store raw file| S3
    API -->|publish UploadEvent| Kafka
    API -->|document status| SQLite
    Kafka -->|consume events| Worker
    Worker -->|download file| S3
    Worker -->|upsert embeddings| Chroma
    Worker -->|update status| SQLite
    Worker -->|retry or dead-letter| Kafka
    Kafka --> DLQ
```

---

## 2) Component Diagram

Internal modules mapped to repository folders.

```mermaid
flowchart TD
    subgraph app["app/ — FastAPI Upload API"]
        Main[main.py]
        Routes[api/upload.py]
        Schemas[schemas/upload.py]
        Config[config.py]
        UploadSvc[services/upload_service.py]
        Storage[services/storage.py]
        KafkaProd[services/kafka_producer.py]
        Idem[services/idempotency.py]
    end

    subgraph worker["worker/ — Ingestion Consumer"]
        WMain[main.py]
        Consumer[consumer.py]
        Handler[handlers/ingestion.py]
        Parser[pipeline/parser.py]
        Chunker[pipeline/chunker.py]
        Embed[pipeline/embeddings.py]
        VStore[pipeline/vector_store.py]
    end

    subgraph shared["shared/ — Domain Models"]
        Models[models.py]
    end

    subgraph infra["Infrastructure"]
        MinIO[(MinIO)]
        Kafka[(Kafka)]
        Chroma[(Chroma)]
        SQLite[(SQLite)]
    end

    Main --> Routes
    Routes --> UploadSvc
    Routes --> Idem
    UploadSvc --> Storage
    UploadSvc --> KafkaProd
    UploadSvc --> Idem
    UploadSvc --> Schemas
    Main --> Config
    Storage --> MinIO
    KafkaProd --> Kafka
    Idem --> SQLite

    WMain --> Consumer
    Consumer --> Handler
    Handler --> Parser
    Handler --> Chunker
    Handler --> Embed
    Handler --> VStore
    Handler --> Storage
    Handler --> Idem
    Handler --> KafkaProd
    Consumer --> Kafka
    VStore --> Chroma
    Handler --> Models
    UploadSvc --> Models
    KafkaProd --> Models
```

---

## 3) Sequence Diagram — Upload (Happy Path)

`POST /api/v1/upload` from client acceptance through Kafka publish.

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI (upload.py)
    participant Svc as UploadService
    participant Idem as IdempotencyStore
    participant S3 as S3Storage / MinIO
    participant Kafka as KafkaEventPublisher
    participant Topic as document.upload

    Client->>API: POST /api/v1/upload (multipart file)
    API->>Svc: upload(file)

    Svc->>Svc: validate extension (.pdf, .docx, .csv)
    Svc->>Svc: read content, reject if empty
    Svc->>Idem: compute_file_hash(content)
    Svc->>Idem: find_by_hash(file_hash)

    alt Duplicate file (same SHA-256)
        Idem-->>Svc: existing DocumentRecord
        Svc-->>API: UploadResponse (is_duplicate=true)
        API-->>Client: 202 + existing document_id
    else New document
        Svc->>Idem: generate_document_id(hash, filename)
        Svc->>S3: upload(s3_key, content, content_type)
        Svc->>Idem: save(DocumentRecord, status=PENDING)
        Svc->>Kafka: publish_upload(UploadEvent)
        Kafka->>Topic: send_and_wait(key=document_id)
        Svc-->>API: UploadResponse (status=accepted)
        API-->>Client: 202 Accepted + document_id
    end
```

---

## 4) Sequence Diagram — Ingestion Worker (Happy Path)

Kafka consumer through parse → chunk → embed → vector store.

```mermaid
sequenceDiagram
    participant Topic as document.upload
    participant Consumer as IngestionConsumer
    participant Handler as IngestionHandler
    participant Idem as IdempotencyStore
    participant S3 as S3Storage
    participant Parser as DocumentParser
    participant Chunker as TextChunker
    participant Embed as EmbeddingProvider
    participant VDB as VectorStore / Chroma

    Topic->>Consumer: UploadEvent message
    Consumer->>Handler: process(event)

    Handler->>Idem: is_indexed(document_id)?
    alt Already indexed
        Handler-->>Consumer: return (ack)
    else Not indexed
        Handler->>VDB: document_exists(document_id)?
        alt Vectors already present
            Handler->>Idem: update_status(INDEXED)
            Handler-->>Consumer: return (ack)
        else Process document
            Handler->>Idem: update_status(PROCESSING)
            Handler->>S3: download(s3_key)
            S3-->>Handler: raw bytes
            Handler->>Parser: parse(content, filename)
            Parser-->>Handler: plain text
            Handler->>Chunker: split(text)
            Chunker-->>Handler: text chunks
            Handler->>Embed: embed(chunks)
            Embed-->>Handler: embedding vectors
            Handler->>VDB: upsert_chunks(document_id, chunks, embeddings)
            VDB-->>Handler: chunk_count
            Handler->>Idem: update_status(INDEXED, chunk_count, indexed_at)
            Handler-->>Consumer: success (ack)
        end
    end
```

---

## 5) Sequence Diagram — Retry and Dead Letter Queue

Failure handling with up to `MAX_RETRIES` (default 3) re-publishes.

```mermaid
sequenceDiagram
    participant Handler as IngestionHandler
    participant Pipeline as Parse/Chunk/Embed/VDB
    participant Kafka as KafkaEventPublisher
    participant Topic as document.upload
    participant DLQ as document.upload.dlq
    participant Idem as IdempotencyStore

    Handler->>Pipeline: process document
    Pipeline-->>Handler: Exception

    Handler->>Handler: retry_count += 1

    alt retry_count < MAX_RETRIES
        Handler->>Kafka: publish_upload(event with retry_count)
        Kafka->>Topic: re-queue event
        Handler->>Idem: update_status(PENDING, error_message)
    else retry_count >= MAX_RETRIES
        Handler->>Kafka: publish_dlq(event, error)
        Kafka->>DLQ: dead-letter message
        Handler->>Idem: update_status(FAILED, error_message)
    end
```

---

## 6) Sequence Diagram — Document Status Polling

`GET /api/v1/documents/{document_id}` for ingestion progress.

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI (upload.py)
    participant Idem as IdempotencyStore
    participant SQLite as SQLite DB

    Client->>API: GET /api/v1/documents/{document_id}
    API->>Idem: get(document_id)
    Idem->>SQLite: SELECT * FROM documents

    alt Document not found
        SQLite-->>Idem: null
        Idem-->>API: null
        API-->>Client: 404 Document not found
    else Document exists
        SQLite-->>Idem: DocumentRecord row
        Idem-->>API: DocumentRecord
        API-->>Client: 200 DocumentStatusResponse
        Note over Client,API: status: pending | processing | indexed | failed
    end
```

---

## 7) Activity Diagram — End-to-End Flow

Full lifecycle from upload request to indexed or failed state.

```mermaid
flowchart TD
    Start([Client uploads file]) --> Validate{Valid extension<br/>and non-empty?}
    Validate -->|No| Reject400[Return 400 Bad Request]
    Validate -->|Yes| Hash[Compute SHA-256 hash]
    Hash --> Dup{Duplicate hash<br/>in SQLite?}
    Dup -->|Yes| ReturnDup[Return existing document_id]
    Dup -->|No| GenId[Generate document_id]
    GenId --> S3Up[Upload to S3/MinIO]
    S3Up --> SavePending[Save status = PENDING]
    SavePending --> PubKafka[Publish Kafka UploadEvent]
    PubKafka --> Accept202[Return 202 Accepted]

    PubKafka --> WorkerStart([Worker consumes event])
    WorkerStart --> IndexedCheck{Already INDEXED<br/>or in Chroma?}
    IndexedCheck -->|Yes| Skip[Skip / Ack message]
    IndexedCheck -->|No| Processing[Set status = PROCESSING]
    Processing --> Download[Download from S3]
    Download --> Parse[Parse PDF / DOCX / CSV]
    Parse --> Chunk[Split into chunks]
    Chunk --> Embed[Generate embeddings]
    Embed --> Upsert[Upsert into Chroma]
    Upsert --> Success{Pipeline OK?}
    Success -->|Yes| MarkIndexed[Set status = INDEXED]
    MarkIndexed --> Done([Ingestion complete])
    Success -->|No| RetryCheck{retry_count < MAX_RETRIES?}
    RetryCheck -->|Yes| Requeue[Re-publish to document.upload]
    Requeue --> Pending[Set status = PENDING + error]
    RetryCheck -->|No| DLQ[Publish to DLQ topic]
    DLQ --> Failed[Set status = FAILED]
    Failed --> EndFail([Ingestion failed])

    Accept202 --> Poll([Client polls GET /documents/id])
    Poll --> ShowStatus[Return current status]
```

---

## 8) State Machine — Document Status

Transitions stored in the SQLite idempotency database.

```mermaid
stateDiagram-v2
    [*] --> pending: Upload accepted / saved

    pending --> processing: Worker starts ingestion
    pending --> pending: Retry re-queued (with error_message)

    processing --> indexed: Parse → chunk → embed → upsert success
    processing --> pending: Failure, retries remaining
    processing --> failed: Failure, max retries exceeded

    indexed --> [*]
    failed --> [*]

    note right of pending
        Client may receive 202 Accepted
        Worker not yet started or retrying
    end note

    note right of indexed
        chunk_count and indexed_at populated
        Vectors available in Chroma
    end note

    note right of failed
        Message sent to document.upload.dlq
        error_message stored in SQLite
    end note
```

---

## 9) Class Diagram — Domain Models

Core Pydantic models in `shared/models.py` and API schemas.

```mermaid
classDiagram
    class DocumentStatus {
        <<enumeration>>
        PENDING
        PROCESSING
        INDEXED
        FAILED
    }

    class UploadEvent {
        +str document_id
        +str s3_key
        +str filename
        +str content_type
        +str file_hash
        +datetime uploaded_at
        +int retry_count
    }

    class DocumentRecord {
        +str document_id
        +str filename
        +str file_hash
        +str s3_key
        +DocumentStatus status
        +datetime created_at
        +datetime indexed_at
        +int chunk_count
        +str error_message
    }

    class UploadResponse {
        +str document_id
        +str status
        +str message
        +bool is_duplicate
    }

    class DocumentStatusResponse {
        +str document_id
        +str filename
        +str status
        +int chunk_count
        +str indexed_at
        +str error_message
    }

    class HealthResponse {
        +str status
        +str service
    }

    DocumentRecord --> DocumentStatus
    UploadEvent ..> DocumentRecord : triggers ingestion of
    UploadResponse ..> DocumentRecord : returns document_id from
    DocumentStatusResponse ..> DocumentRecord : maps from
```

---

## 10) Deployment Diagram — Docker Compose Stack

Local and containerized runtime topology.

```mermaid
flowchart TB
    subgraph Client
        Curl[curl / HTTP Client]
    end

    subgraph DockerCompose["docker compose"]
        subgraph APIPod["api service :8100"]
            FastAPI[uvicorn app.main:app]
        end

        subgraph WorkerPod["worker service"]
            WorkerProc[python -m worker.main]
        end

        subgraph Messaging
            ZK[Zookeeper :2181]
            Kafka[Kafka :9092]
        end

        subgraph ObjectStore
            MinIO[MinIO :9000 / :9001]
        end
    end

    subgraph HostVolumes["Host-mounted / local paths"]
        ChromaData[./chroma_data]
        IdemDB[./data/idempotency.db]
    end

    Curl -->|POST /api/v1/upload| FastAPI
    Curl -->|GET /api/v1/documents/id| FastAPI
    Curl -->|GET /health| FastAPI

    FastAPI --> MinIO
    FastAPI --> Kafka
    FastAPI --> IdemDB

    WorkerProc --> Kafka
    WorkerProc --> MinIO
    WorkerProc --> ChromaData
    WorkerProc --> IdemDB
    WorkerProc -->|DLQ on failure| Kafka

    Kafka --> ZK
```

---

## 11) Package / Folder Dependency View

Repository layout and import direction.

```mermaid
flowchart LR
    subgraph API["app/"]
        A1[main.py]
        A2[api/upload.py]
        A3[services/*]
        A4[schemas/upload.py]
        A5[config.py]
    end

    subgraph Worker["worker/"]
        W1[main.py]
        W2[consumer.py]
        W3[handlers/ingestion.py]
        W4[pipeline/*]
    end

    subgraph Shared["shared/"]
        S1[models.py]
    end

    subgraph Docs["docs/"]
        D1[architecture.md]
        D2[uml-artifacts.md]
    end

    subgraph Tests["tests/"]
        T1[test_upload.py]
        T2[test_pipeline.py]
    end

    A1 --> A2 --> A3
    A3 --> S1
    A2 --> A4
    A3 --> A5

    W1 --> W2 --> W3 --> W4
    W3 --> A3
    W3 --> S1
    W2 --> S1

    T1 --> A3
    T2 --> A1
    T2 --> W4

    D1 -. documents .-> D2
```

---

## 12) Data Flow Diagram — Ingestion Pipeline Stages

How raw bytes become searchable vectors.

```mermaid
flowchart LR
    subgraph Input
        File[Uploaded File<br/>.pdf / .docx / .csv]
    end

    subgraph Storage
        S3Key[S3 Key<br/>uploads/id/filename]
    end

    subgraph Parse["worker/pipeline/parser.py"]
        Text[Plain Text]
    end

    subgraph Chunk["worker/pipeline/chunker.py"]
        Chunks[Text Chunks<br/>size=1000, overlap=200]
    end

    subgraph Embed["worker/pipeline/embeddings.py"]
        Vectors[384-dim Vectors<br/>deterministic dev embeddings]
    end

    subgraph Index["worker/pipeline/vector_store.py"]
        ChromaRec[Chroma Records<br/>id, document, embedding, metadata]
    end

    File --> S3Key
    S3Key -->|download| Text
    Text --> Chunks
    Chunks --> Vectors
    Vectors --> ChromaRec
```

---

## 13) API Endpoint Map

```mermaid
flowchart TD
    Root[FastAPI App]

    Root --> Health["GET /health"]
    Root --> Upload["POST /api/v1/upload"]
    Root --> Status["GET /api/v1/documents/{document_id}"]

    Health --> HR[HealthResponse<br/>status, service]
    Upload --> UR[UploadResponse<br/>document_id, status, message, is_duplicate]
    Status --> DSR[DocumentStatusResponse<br/>status, chunk_count, indexed_at, error]

    Upload -->|202 Accepted| Queue[Kafka document.upload]
    Queue --> Worker[Ingestion Worker]
    Status -->|reads| DB[(SQLite idempotency.db)]
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [architecture.md](./architecture.md) | Narrative architecture and primary sequence diagram |
| [../README.md](../README.md) | Quick start, Docker, curl examples |
| [../.env.example](../.env.example) | Environment variable reference |

---

## Diagram Index

| # | Diagram | Type | Scope |
|---|---------|------|-------|
| 1 | System Context | C4 / Context | External systems |
| 2 | Component | Component | `app/`, `worker/`, `shared/` |
| 3 | Upload Happy Path | Sequence | API upload flow |
| 4 | Ingestion Happy Path | Sequence | Worker pipeline |
| 5 | Retry & DLQ | Sequence | Failure handling |
| 6 | Status Polling | Sequence | GET document status |
| 7 | End-to-End Activity | Activity | Full lifecycle |
| 8 | Document Status | State Machine | Status transitions |
| 9 | Domain Models | Class | Pydantic schemas |
| 10 | Docker Compose | Deployment | Infrastructure |
| 11 | Folder Dependencies | Package | Repo structure |
| 12 | Pipeline Data Flow | Data Flow | Parse → index |
| 13 | API Endpoint Map | Component | HTTP surface |
