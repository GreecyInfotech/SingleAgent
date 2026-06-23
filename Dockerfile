FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip hatchling \
    && pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.11-slim AS runtime

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY src/ ./src/
COPY agents/ ./agents/
COPY orchestrator/ ./orchestrator/
COPY rag/ ./rag/
COPY mcp_servers/ ./mcp_servers/
COPY mcp-servers/ ./mcp-servers/
COPY tools/ ./tools/
COPY services/ ./services/

RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src:/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "enterprise_agent_platform.main:app", "--host", "0.0.0.0", "--port", "8000"]
