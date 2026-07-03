from typing import Any

from mcp_servers.shared.base_server import DeclarativeMCPServer


class SalesforceMCPServer(DeclarativeMCPServer):
    name = "salesforce"
    version = "1.0.0"
    TOOL_DEFINITIONS = [
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

    def _build_tool_handlers(self):
        return {
            "query_soql": self._query_soql,
            "get_account": self._get_account,
            "create_lead": self._create_lead,
        }

    async def _query_soql(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"records": [], "totalSize": 0, "soql": arguments["soql"]}

    async def _get_account(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"Id": arguments["account_id"], "Name": "Acme Corp", "Industry": "Technology"}

    async def _create_lead(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"Id": "00Q000001", **arguments, "Status": "Open"}
