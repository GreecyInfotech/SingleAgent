# Document RAG System

Production-ready document upload and RAG ingestion pipeline with FastAPI, Kafka, S3, and Chroma vector store.

## Architecture

Matches the end-to-end flow:

1. **FastAPI Upload API** — validate, idempotency, S3 upload, Kafka publish, `202 Accepted`
2. **Kafka Queue** — async event bridge
3. **Ingestion Worker** — download, parse, chunk, embed, vector store, mark processed
4. **Retry + DLQ** — up to 3 retries, then dead-letter queue

See `docs/architecture.md` for diagrams and `docs/uml-artifacts.md` for the full UML artifact set.

## Quick Start

```bash
cd D:\personal\SingleAgent\documentragsystem
copy .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

# Start infrastructure (Kafka + MinIO)
docker compose up -d zookeeper kafka minio

# Terminal 1: API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8100

# Terminal 2: Worker
python -m worker.main
```

## Upload a Document

```bash
curl -X POST "http://localhost:8100/api/v1/upload" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@sample.pdf"
```

Check status:

```bash
curl http://localhost:8100/api/v1/documents/{document_id}
```

## Full Stack (Docker)

```bash
docker compose up --build
```

Services:
- API: `http://localhost:8100`
- MinIO Console: `http://localhost:9001` (minioadmin/minioadmin)
- Kafka: `localhost:9092`

## Project Structure

```
documentragsystem/
├── app/                  # FastAPI upload API
│   ├── api/              # Routes
│   ├── services/         # S3, Kafka, idempotency, upload logic
│   └── schemas/          # Request/response models
├── worker/               # Ingestion consumer
│   ├── pipeline/         # Parse, chunk, embed, vector store
│   └── handlers/         # Ingestion orchestration
├── shared/               # Domain models and events
├── docs/                 # Architecture documentation
└── tests/                # Test suite
```

## Test

```bash
pytest -q
```

## Supported Formats

- `.pdf`
- `.docx`
- `.csv`
