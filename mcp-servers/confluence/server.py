from typing import Any

from mcp_servers.shared.base_server import DeclarativeMCPServer


class ConfluenceMCPServer(DeclarativeMCPServer):
    name = "confluence"
    version = "1.0.0"
    TOOL_DEFINITIONS = [
        {
            "name": "search_pages",
            "description": "Search Confluence pages",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "space": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "get_page",
            "description": "Get page content by ID",
            "inputSchema": {
                "type": "object",
                "properties": {"page_id": {"type": "string"}},
                "required": ["page_id"],
            },
        },
    ]

    def _build_tool_handlers(self):
        return {
            "search_pages": self._search_pages,
            "get_page": self._get_page,
        }

    async def _search_pages(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"pages": [{"id": "1", "title": f"Results for: {arguments['query']}"}]}

    async def _get_page(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"id": arguments["page_id"], "content": "<p>Page content</p>"}
