from typing import Any

from pydantic import BaseModel, Field


class AgentExecuteRequest(BaseModel):
    customer_id: str | None = None
    user_id: str | None = None
    query: str = ""
    context: dict[str, Any] = Field(default_factory=dict)

    def to_input(self) -> dict[str, Any]:
        data = self.model_dump(exclude_none=True)
        data.update(self.context)
        data.pop("context", None)
        return data


class OrchestrateRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: dict[str, Any] | None = None


class MCPToolRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)
