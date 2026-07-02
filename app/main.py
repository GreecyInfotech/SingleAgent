from __future__ import annotations

import time

import structlog
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from agents.planner import plan_response
from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from observability.metrics.registry import LATENCY_SECONDS, REQUESTS_TOTAL
from security.input_guard import is_safe_user_input
from services.router import route_query

logger = structlog.get_logger()

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    path = request.url.path
    method = request.method
    REQUESTS_TOTAL.labels(path=path, method=method, status=str(response.status_code)).inc()
    LATENCY_SECONDS.labels(path=path, method=method).observe(elapsed)
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "UP", "service": settings.app_name}


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {"status": "READY"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    if not is_safe_user_input(payload.message):
        raise HTTPException(status_code=400, detail="Blocked unsafe input.")
    route, context = route_query(payload.message)
    answer, confidence = plan_response(route, payload.message, context)
    logger.info("chat_processed", route=route, confidence=confidence, session_id=payload.session_id)
    return ChatResponse(answer=answer, confidence=confidence, route=route)
