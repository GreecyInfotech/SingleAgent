from typing import Any

from mcp_servers.shared.base_server import DeclarativeMCPServer


class SAPMCPServer(DeclarativeMCPServer):
    name = "sap"
    version = "1.0.0"
    TOOL_DEFINITIONS = [
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

    def _build_tool_handlers(self):
        return {
            "get_material": self._get_material,
            "get_purchase_order": self._get_purchase_order,
        }

    async def _get_material(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"MATNR": arguments["material_id"], "MAKTX": "Enterprise Widget", "MEINS": "EA"}

    async def _get_purchase_order(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"EBELN": arguments["po_number"], "STATUS": "RELEASED", "NETWR": 15000.00}
