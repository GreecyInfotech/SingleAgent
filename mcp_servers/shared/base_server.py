from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Awaitable, Callable

ToolHandler = Callable[[dict[str, Any]], Awaitable[Any]]


class MCPServerBase(ABC):
    """Base class for Model Context Protocol servers."""

    name: str = "base"
    version: str = "1.0.0"

    _tools_cache: list[dict[str, Any]] | None = None
    _schema_index: dict[str, dict[str, Any]] | None = None
    _handlers_cache: dict[str, ToolHandler] | None = None

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Subclasses must define tool schemas.")

    def get_tool_handlers(self) -> dict[str, ToolHandler]:
        if self._handlers_cache is None:
            self._handlers_cache = self._build_tool_handlers()
        return self._handlers_cache

    @abstractmethod
    def _build_tool_handlers(self) -> dict[str, ToolHandler]:
        raise NotImplementedError("Subclasses must define tool handlers.")

    async def list_tools(self) -> list[dict[str, Any]]:
        if self._tools_cache is None:
            self._tools_cache = self.get_tool_definitions()
        return deepcopy(self._tools_cache)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        handlers = self.get_tool_handlers()
        if name not in handlers:
            available = ", ".join(sorted(handlers))
            raise ValueError(f"Unknown tool: {name}. Available: {available}")

        tool_schema = self._tool_schema(name)
        self._validate_required_arguments(tool_schema, arguments)
        return await handlers[name](arguments)

    def _tool_schema(self, name: str) -> dict[str, Any]:
        if self._schema_index is None:
            self._schema_index = {tool["name"]: tool for tool in self.get_tool_definitions()}
        try:
            return self._schema_index[name]
        except KeyError as exc:
            raise ValueError(f"Unknown tool schema: {name}") from exc

    @staticmethod
    def _validate_required_arguments(tool_schema: dict[str, Any], arguments: dict[str, Any]) -> None:
        required = tool_schema.get("inputSchema", {}).get("required", [])
        missing = [key for key in required if key not in arguments]
        if missing:
            raise ValueError(f"Missing required arguments: {', '.join(missing)}")

    def get_server_info(self) -> dict[str, str]:
        return {"name": self.name, "version": self.version, "protocol": "mcp"}


class DeclarativeMCPServer(MCPServerBase):
    """MCP server with class-level tool definitions and handler registration."""

    TOOL_DEFINITIONS: list[dict[str, Any]] = []

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        return self.TOOL_DEFINITIONS
