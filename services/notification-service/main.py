from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Notification Service", version="1.0.0")


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class NotificationRequest(BaseModel):
    channel: NotificationChannel
    recipient: str
    subject: str = ""
    body: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Notification(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    status: str = "sent"
    sent_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


@app.post("/notifications/send", response_model=Notification, status_code=201)
async def send_notification(request: NotificationRequest) -> Notification:
    return Notification(
        channel=request.channel,
        recipient=request.recipient,
        subject=request.subject,
        body=request.body,
    )


@app.post("/notifications/bulk")
async def send_bulk(
    requests: list[NotificationRequest],
) -> dict:
    notifications = [
        Notification(
            channel=r.channel,
            recipient=r.recipient,
            subject=r.subject,
            body=r.body,
        )
        for r in requests
    ]
    return {"sent": len(notifications), "notifications": notifications}


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "service": "notification-service"}
