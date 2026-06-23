from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from enterprise_agent_platform.domain.models import AgentStatus, ConversationStatus, MessageRole

# --- Agent DTOs ---


class CreateAgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    system_prompt: str = Field(..., min_length=1)
    model: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateAgentRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=128000)
    tools: list[str] | None = None
    status: AgentStatus | None = None
    metadata: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    id: UUID
    name: str
    description: str
    system_prompt: str
    model: str
    temperature: float
    max_tokens: int
    tools: list[str]
    status: AgentStatus
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# --- Conversation DTOs ---


class CreateConversationRequest(BaseModel):
    agent_id: UUID
    user_id: str | None = None
    title: str = "New Conversation"
    metadata: dict[str, Any] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    metadata: dict[str, Any]
    created_at: datetime


class ConversationResponse(BaseModel):
    id: UUID
    agent_id: UUID
    user_id: str | None
    title: str
    status: ConversationStatus
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ChatResponse(BaseModel):
    conversation: ConversationResponse
    user_message: MessageResponse
    assistant_message: MessageResponse
    tool_calls_made: list[str]
    tokens_used: int
    latency_ms: float


# --- Tool DTOs ---


class ToolResponse(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]


# --- Common ---


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    skip: int
    limit: int


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    redis: str
