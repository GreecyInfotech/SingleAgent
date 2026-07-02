from typing import Any

from mcp_servers.shared.base_server import MCPServerBase


class SalesforceMCPServer(MCPServerBase):
    name = "salesforce"
    version = "1.0.0"

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "query_soql",
                "description": "Execute SOQL query",
                "inputSchema": {
                    "type": "object",
                    "properties": {"soql": {"type": "string"}},
                    "required": ["soql"],
                },
            },
            {
                "name": "get_account",
                "description": "Get Salesforce account by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {"account_id": {"type": "string"}},
                    "required": ["account_id"],
                },
            },
            {
                "name": "create_lead",
                "description": "Create a new lead",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "company": {"type": "string"},
                        "email": {"type": "string"},
                    },
                    "required": ["last_name", "company"],
                },
            },
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "query_soql":
            return {"records": [], "totalSize": 0}
        if name == "get_account":
            return {"Id": arguments["account_id"], "Name": "Acme Corp", "Industry": "Technology"}
        if name == "create_lead":
            return {"Id": "00Q000001", **arguments, "Status": "Open"}
        raise ValueError(f"Unknown tool: {name}")
