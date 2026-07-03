from typing import Any

from mcp_servers.shared.base_server import DeclarativeMCPServer


class OracleMCPServer(DeclarativeMCPServer):
    name = "oracle"
    version = "1.0.0"
    TOOL_DEFINITIONS = [
        {
            "name": "execute_query",
            "description": "Execute read-only SQL query",
            "inputSchema": {
                "type": "object",
                "properties": {"sql": {"type": "string"}, "bind_params": {"type": "object"}},
                "required": ["sql"],
            },
        },
        {
            "name": "get_customer",
            "description": "Get customer record from Oracle ERP",
            "inputSchema": {
                "type": "object",
                "properties": {"customer_id": {"type": "string"}},
                "required": ["customer_id"],
            },
        },
    ]

    def _build_tool_handlers(self):
        return {
            "execute_query": self._execute_query,
            "get_customer": self._get_customer,
        }

    async def _execute_query(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"rows": [], "rowCount": 0, "sql": arguments["sql"]}

    async def _get_customer(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {
            "CUSTOMER_ID": arguments["customer_id"],
            "NAME": "Enterprise Customer",
            "CREDIT_LIMIT": 100000,
        }
