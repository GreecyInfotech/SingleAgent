from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Audit Service", version="1.0.0")


class AuditAction(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    LOGIN = "login"


class AuditEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: str | None = None
    user_agent: str | None = None


_EVENTS: list[AuditEvent] = []


@app.post("/audit/events", response_model=AuditEvent, status_code=201)
async def log_event(event: AuditEvent) -> AuditEvent:
    _EVENTS.append(event)
    return event


@app.get("/audit/events", response_model=list[AuditEvent])
async def query_events(
    actor_id: str | None = None,
    resource_type: str | None = None,
    action: AuditAction | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[AuditEvent]:
    results = _EVENTS
    if actor_id:
        results = [e for e in results if e.actor_id == actor_id]
    if resource_type:
        results = [e for e in results if e.resource_type == resource_type]
    if action:
        results = [e for e in results if e.action == action]
    return results[skip : skip + limit]


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "audit-service", "events_logged": len(_EVENTS)}
