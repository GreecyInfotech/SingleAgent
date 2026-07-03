from typing import Any

from mcp_servers.shared.base_server import DeclarativeMCPServer


class PostgresMCPServer(DeclarativeMCPServer):
    name = "postgres"
    version = "1.0.0"
    TOOL_DEFINITIONS = [
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

    def __init__(self, connection_string: str = "") -> None:
        self._connection_string = connection_string

    def _build_tool_handlers(self):
        return {
            "query": self._query,
            "list_tables": self._list_tables,
        }

    async def _query(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"rows": [], "rowCount": 0, "sql": arguments["sql"]}

    async def _list_tables(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "tables": ["agents", "conversations", "messages", "users", "audit_logs"],
            "schema": arguments.get("schema", "public"),
        }
