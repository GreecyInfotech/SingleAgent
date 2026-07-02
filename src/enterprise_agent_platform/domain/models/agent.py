from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from enterprise_agent_platform.domain.models.enums import AgentStatus


class Agent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    system_prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: list[str] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.ACTIVE
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"from_attributes": True}
