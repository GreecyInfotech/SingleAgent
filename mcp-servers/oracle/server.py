from typing import Any

from mcp_servers.shared.base_server import MCPServerBase


class OracleMCPServer(MCPServerBase):
    name = "oracle"
    version = "1.0.0"

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
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

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "execute_query":
            return {"rows": [], "rowCount": 0}
        if name == "get_customer":
            return {
                "CUSTOMER_ID": arguments["customer_id"],
                "NAME": "Enterprise Customer",
                "CREDIT_LIMIT": 100000,
            }
        raise ValueError(f"Unknown tool: {name}")
