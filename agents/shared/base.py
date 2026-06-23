from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from agents.shared.services import agent_services


class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: list[str] = Field(default_factory=list)
    mcp_servers: list[str] = Field(default_factory=list)
    rag_enabled: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class BaseEnterpriseAgent(ABC):
    """Base class for all enterprise domain agents."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self._services = agent_services

    @property
    def name(self) -> str:
        return self.config.name

    @abstractmethod
    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input and return agent response."""

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        return []

    async def invoke_mcp(
        self, server_name: str, tool_name: str, arguments: dict[str, Any]
    ) -> Any:
        if server_name not in self.config.mcp_servers:
            raise ValueError(f"MCP server '{server_name}' not enabled for {self.name}")
        return await self._services.call_mcp(server_name, tool_name, arguments)

    async def search_knowledge(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.config.rag_enabled:
            return []
        return await self._services.search_knowledge(query, limit=limit)

    async def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        return await self._services.search(query, limit=limit)

    def to_platform_agent(self) -> dict[str, Any]:
        return {
            "name": self.config.name,
            "description": self.config.description,
            "system_prompt": self.config.system_prompt,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "tools": self.config.tools,
            "metadata": {
                **self.config.metadata,
                "mcp_servers": self.config.mcp_servers,
                "rag_enabled": self.config.rag_enabled,
            },
        }

    def _build_response(
        self,
        *,
        input_data: dict[str, Any],
        response: str,
        confidence: float,
        actions: list[str],
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "agent": self.name,
            "response": response,
            "confidence": confidence,
            "actions": actions,
            "tools_used": self.config.tools,
            "mcp_servers": self.config.mcp_servers,
        }
        if extra:
            payload.update(extra)
        payload["input"] = {k: v for k, v in input_data.items() if k != "query"}
        return payload
