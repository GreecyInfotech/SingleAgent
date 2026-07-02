from abc import ABC, abstractmethod
from typing import Any


class MCPServerBase(ABC):
    """Base class for Model Context Protocol servers."""

    name: str = "base"
    version: str = "1.0.0"

    @abstractmethod
    async def list_tools(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any: ...

    def get_server_info(self) -> dict[str, str]:
        return {"name": self.name, "version": self.version, "protocol": "mcp"}
