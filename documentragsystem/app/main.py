from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.config import get_settings
from app.schemas.upload import HealthResponse
from app.services.kafka_producer import kafka_publisher

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await kafka_publisher.start()
    logger.info("api_started", service=settings.app_name)
    yield
    await kafka_publisher.stop()
    logger.info("api_stopped")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Document upload API for RAG ingestion pipeline",
    lifespan=lifespan,
)

app.include_router(upload_router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="UP", service=settings.app_name)
