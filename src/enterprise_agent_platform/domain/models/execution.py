from uuid import UUID

from pydantic import BaseModel, Field

from enterprise_agent_platform.domain.models.message import Message


class AgentExecutionResult(BaseModel):
    conversation_id: UUID
    message: Message
    tool_calls_made: list[str] = Field(default_factory=list)
    tokens_used: int = 0
    latency_ms: float = 0.0

    model_config = {"from_attributes": True}
