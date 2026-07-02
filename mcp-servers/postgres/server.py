from typing import Any

from mcp_servers.shared.base_server import MCPServerBase


class PostgresMCPServer(MCPServerBase):
    name = "postgres"
    version = "1.0.0"

    def __init__(self, connection_string: str = "") -> None:
        self._connection_string = connection_string

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "query",
                "description": "Execute a read-only SQL query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string"},
                        "params": {"type": "array", "items": {}},
                    },
                    "required": ["sql"],
                },
            },
            {
                "name": "list_tables",
                "description": "List tables in a schema",
                "inputSchema": {
                    "type": "object",
                    "properties": {"schema": {"type": "string", "default": "public"}},
                },
            },
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "query":
            return {"rows": [], "rowCount": 0, "sql": arguments["sql"]}
        if name == "list_tables":
            return {"tables": ["agents", "conversations", "messages", "users", "audit_logs"]}
        raise ValueError(f"Unknown tool: {name}")
