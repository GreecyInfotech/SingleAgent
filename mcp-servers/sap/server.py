from typing import Any

from mcp_servers.shared.base_server import MCPServerBase


class SAPMCPServer(MCPServerBase):
    name = "sap"
    version = "1.0.0"

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "get_material",
                "description": "Get SAP material master data",
                "inputSchema": {
                    "type": "object",
                    "properties": {"material_id": {"type": "string"}},
                    "required": ["material_id"],
                },
            },
            {
                "name": "get_purchase_order",
                "description": "Get purchase order details",
                "inputSchema": {
                    "type": "object",
                    "properties": {"po_number": {"type": "string"}},
                    "required": ["po_number"],
                },
            },
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "get_material":
            return {"MATNR": arguments["material_id"], "MAKTX": "Enterprise Widget", "MEINS": "EA"}
        if name == "get_purchase_order":
            return {"EBELN": arguments["po_number"], "STATUS": "RELEASED", "NETWR": 15000.00}
        raise ValueError(f"Unknown tool: {name}")
