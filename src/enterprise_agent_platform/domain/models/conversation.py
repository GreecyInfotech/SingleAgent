from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from enterprise_agent_platform.domain.models.enums import ConversationStatus


class Conversation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    agent_id: UUID
    user_id: str | None = None
    title: str = "New Conversation"
    status: ConversationStatus = ConversationStatus.ACTIVE
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"from_attributes": True}
