FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
COPY services ./services
COPY agents ./agents
COPY retrieval ./retrieval
COPY security ./security
COPY observability ./observability

RUN pip install --no-cache-dir .

RUN groupadd --gid 10001 appuser && useradd --uid 10001 --gid appuser --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
